import requests
import stripe
from flask.ext.restplus import abort
from flask_admin import BaseView, expose
from flask import redirect, url_for, request, jsonify, make_response, flash
from xhtml2pdf import pisa
from cStringIO import StringIO

import pycountry

from app import get_settings
from app.helpers.ticketing import TicketingManager

def create_pdf(pdf_data):
    pdf = StringIO()
    pisa.CreatePDF(StringIO(pdf_data.encode('utf-8')), pdf)
    return pdf

class TicketingView(BaseView):
    @expose('/', methods=('GET',))
    def index(self):
        return redirect("/")

    @expose('/create/', methods=('POST', ))
    def create_order(self):
        order = TicketingManager.create_order(request.form)
        if request.form.get('promo_code', '') != '':
            flash('The promotional code entered is valid. No offer has been applied to this order.', 'danger')
        return redirect(url_for('.view_order', order_identifier=order.identifier))

    @expose('/<order_identifier>/', methods=('GET',))
    def view_order(self, order_identifier):
        order = TicketingManager.get_and_set_expiry(order_identifier)
        if not order or order.status == 'expired':
            abort(404)
        if order.status == 'completed':
            return redirect(url_for('ticketing.view_order_after_payment', order_identifier=order_identifier))

        if order.event.stripe:
            stripe_publishable_key = order.event.stripe.stripe_publishable_key
        else:
            stripe_publishable_key = "No Key Set"

        return self.render('/gentelella/guest/ticketing/order_pre_payment.html', order=order, event=order.event,
                           countries=list(pycountry.countries),
                           stripe_publishable_key=stripe_publishable_key)

    @expose('/<order_identifier>/view/', methods=('GET',))
    def view_order_after_payment(self, order_identifier):
        order = TicketingManager.get_and_set_expiry(order_identifier)
        if not order or order.status != 'completed':
            abort(404)
        return self.render('/gentelella/guest/ticketing/order_post_payment.html', order=order, event=order.event)

    @expose('/<order_identifier>/view/pdf/', methods=('GET',))
    def view_order_after_payment_pdf(self, order_identifier):
        order = TicketingManager.get_and_set_expiry(order_identifier)
        if not order or order.status != 'completed':
            abort(404)
        pdf = create_pdf(self.render('/gentelella/guest/ticketing/invoice_pdf.html',
                                     order=order, event=order.event))
        response = make_response(pdf.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = \
            'inline; filename=%s.pdf' % order.get_invoice_number()
        return response

    @expose('/initiate/payment/', methods=('POST',))
    def initiate_order_payment(self):
        result = TicketingManager.initiate_order_payment(request.form)
        if result:
            return jsonify({
                "status": "ok",
                "email": result.user.email,
                "order_status": result.status
            })
        else:
            return jsonify({
                "status": "error"
            })

    @expose('/charge/payment/', methods=('POST',))
    def charge_order_payment(self):
        result = TicketingManager.charge_order_payment(request.form)
        if result:
            return jsonify({
                "status": "ok"
            })
        else:
            return jsonify({
                "status": "error"
            })

    @expose('/expire/<order_identifier>/', methods=('POST',))
    def expire_order(self, order_identifier):
        TicketingManager.get_and_set_expiry(order_identifier)
        return jsonify({
            "status": "ok"
        })

    @expose('/stripe/callback/', methods=('GET',))
    def stripe_callback(self):
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
                return self.render('/gentelella/guest/ticketing/stripe_oauth_callback.html', response=response_json,
                                   account=account)

        return "Error"
