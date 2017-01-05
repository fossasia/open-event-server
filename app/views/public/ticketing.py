from cStringIO import StringIO

import pycountry
import requests
import stripe
from flask import Blueprint
from flask import redirect, url_for, request, jsonify, make_response, flash
from flask import render_template
from flask.ext.restplus import abort
from xhtml2pdf import pisa

from app import get_settings
from app.helpers.data import save_to_db
from app.helpers.payment import PayPalPaymentsManager
from app.helpers.ticketing import TicketingManager


def create_pdf(pdf_data):
    pdf = StringIO()
    pisa.CreatePDF(StringIO(pdf_data.encode('utf-8')), pdf)
    return pdf


ticketing = Blueprint('ticketing', __name__, url_prefix='/orders')


@ticketing.route('/', methods=('GET',))
def index():
    return redirect("/")


@ticketing.route('/create/', methods=('POST',))
def create_order():
    order = TicketingManager.create_order(request.form)
    return redirect(url_for('.view_order', order_identifier=order.identifier))


@ticketing.route('/<order_identifier>/', methods=('GET',))
def view_order(order_identifier):
    order = TicketingManager.get_and_set_expiry(order_identifier)
    if not order or order.status == 'expired' or order.status == 'placed':
        abort(404)
    if order.status == 'completed':
        return redirect(url_for('ticketing.view_order_after_payment', order_identifier=order_identifier))

    if order.event.stripe:
        stripe_publishable_key = order.event.stripe.stripe_publishable_key
    else:
        stripe_publishable_key = "No Key Set"

    return render_template('gentelella/guest/ticketing/order_pre_payment.html', order=order, event=order.event,
                           countries=list(pycountry.countries),
                           stripe_publishable_key=stripe_publishable_key)


@ticketing.route('/<order_identifier>/view/', methods=('GET',))
def view_order_after_payment(order_identifier):
    order = TicketingManager.get_and_set_expiry(order_identifier)
    if not order or (order.status != 'completed' and order.status != 'placed'):
        abort(404)
    flash("An email with the ticket has also been sent to your email account.")
    return render_template('gentelella/guest/ticketing/order_post_payment.html', order=order, event=order.event)


@ticketing.route('/<order_identifier>/view/pdf/', methods=('GET',))
def view_order_after_payment_pdf(order_identifier):
    order = TicketingManager.get_and_set_expiry(order_identifier)
    if not order or order.status != 'completed':
        abort(404)
    pdf = create_pdf(render_template('gentelella/guest/ticketing/invoice_pdf.html',
                                     order=order, event=order.event))
    response = make_response(pdf.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = \
        'inline; filename=%s.pdf' % order.get_invoice_number()
    return response


@ticketing.route('/<order_identifier>/view/tickets/pdf/', methods=('GET',))
def view_order_tickets_after_payment_pdf(order_identifier):
    order = TicketingManager.get_and_set_expiry(order_identifier)
    if not order or order.status != 'completed':
        abort(404)
    pdf = create_pdf(render_template('gentelella/guest/ticketing/pdf/ticket.html', order=order))
    response = make_response(pdf.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = \
        'inline; filename=%s.pdf' % "test"
    return response


@ticketing.route('/initiate/payment/', methods=('POST',))
def initiate_order_payment():
    paid_via = request.form.get('pay_via_service', 'stripe')
    result = TicketingManager.initiate_order_payment(request.form, paid_via)
    if result:
        if request.form.get('pay_via_service', 'stripe') != 'paypal':
            return jsonify({
                "status": "ok",
                "email": result.user.email,
                "action": "start_stripe"
                if result.status == 'initialized' and paid_via == 'stripe'
                else "show_completed"
            })
        else:
            return jsonify({
                "status": "ok",
                "email": result.user.email,
                "action": "start_paypal",
                "redirect_url": PayPalPaymentsManager.get_checkout_url(result)
            })
    else:
        return jsonify({
            "status": "error"
        })


@ticketing.route('/charge/payment/', methods=('POST',))
def charge_stripe_order_payment():
    status, result = TicketingManager.charge_stripe_order_payment(request.form)
    if status:
        return jsonify({
            "status": "ok",
            "message": result.transaction_id
        })
    else:
        return jsonify({
            "status": "error",
            "message": result
        })


@ticketing.route('/expire/<order_identifier>/', methods=('POST',))
def expire_order(order_identifier):
    TicketingManager.get_and_set_expiry(order_identifier)
    return jsonify({
        "status": "ok"
    })


@ticketing.route('/stripe/callback/', methods=('GET',))
def stripe_callback():
    code = request.args.get('code')
    if code and code != "":
        data = {
            'client_secret': get_settings()['stripe_secret_key'],
            'code': code,
            'grant_type': 'authorization_code'
        }
        response = requests.post('https://connect.stripe.com/oauth/token', data=data)
        if response.status_code == 200:
            response_json = response.json()
            stripe.api_key = response_json['access_token']
            account = stripe.Account.retrieve(response_json['stripe_user_id'])
            return render_template('gentelella/guest/ticketing/stripe_oauth_callback.html', response=response_json,
                                   account=account)
    return "Error"


@ticketing.route('/<order_identifier>/error/', methods=('GET', 'POST'))
def show_transaction_error(order_identifier):
    order = TicketingManager.get_order_by_identifier(order_identifier)
    return render_template('gentelella/guest/ticketing/order_post_payment_error.html', order=order,
                           event=order.event)


@ticketing.route('/<order_identifier>/paypal/<function>/', methods=('GET',))
def paypal_callback(order_identifier, function):
    order = TicketingManager.get_order_by_identifier(order_identifier)
    if not order or order.status == 'expired':
        abort(404)
    if function == 'cancel':
        order.status = 'expired'
        save_to_db(order)
        return redirect(url_for('event_detail.display_event_detail_home', identifier=order.event.identifier))
    elif function == 'success':
        status, result = TicketingManager.charge_paypal_order_payment(order)
        if status:
            return redirect(url_for('.view_order', order_identifier=order_identifier))
        else:
            flash("An error occurred while processing your transaction. " + str(result), "danger")
            return redirect(url_for('.show_transaction_error', order_identifier=order_identifier))
    abort(404)
