from StringIO import StringIO
from flask import make_response

import pycountry
import re
from datetime import datetime
from flask import Blueprint
from flask import abort, jsonify
from flask import redirect, flash
from flask import request, render_template
from flask import url_for

from xhtml2pdf import pisa

from app import get_settings
from app.helpers.cache import cache
from app.helpers.data import delete_from_db
from app.helpers.data import save_to_db
from app.helpers.data_getter import DataGetter
from app.helpers.ticketing import TicketingManager
from app.models.ticket import Ticket

event_ticket_sales = Blueprint('event_ticket_sales', __name__, url_prefix='/events/<int:event_id>/tickets')


def create_pdf(pdf_data):
    pdf = StringIO()
    pisa.CreatePDF(StringIO(pdf_data.encode('utf-8')), pdf)
    return pdf


@cache.memoize(50)
def get_ticket(ticket_id):
    return Ticket.query.get(ticket_id)


@event_ticket_sales.route('/')
def display_ticket_stats(event_id):
    event = DataGetter.get_event(event_id)
    orders = TicketingManager.get_orders(event_id)

    orders_summary = {
        'completed': {
            'class': 'success',
            'tickets_count': 0,
            'orders_count': 0,
            'total_sales': 0
        },
        'placed': {
            'class': 'info',
            'tickets_count': 0,
            'orders_count': 0,
            'total_sales': 0
        },
        'pending': {
            'class': 'warning',
            'tickets_count': 0,
            'orders_count': 0,
            'total_sales': 0
        },
        'expired': {
            'class': 'danger',
            'tickets_count': 0,
            'orders_count': 0,
            'total_sales': 0
        },
        'deleted': {
            'class': 'primary',
            'tickets_count': 0,
            'orders_count': 0,
            'total_sales': 0
        },
        'cancelled': {
            'class': 'default',
            'tickets_count': 0,
            'orders_count': 0,
            'total_sales': 0
        }
    }

    tickets_summary = {}

    for ticket in event.tickets:
        tickets_summary[str(ticket.id)] = {
            'name': ticket.name,
            'quantity': ticket.quantity,
            'completed': {
                'tickets_count': 0,
                'sales': 0
            },
            'placed': {
                'tickets_count': 0,
                'sales': 0
            },
            'pending': {
                'tickets_count': 0,
                'sales': 0
            },
            'expired': {
                'class': 'danger',
                'tickets_count': 0,
                'sales': 0
            },
            'deleted': {
                'tickets_count': 0,
                'sales': 0
            },
            'cancelled': {
                'tickets_count': 0,
                'sales': 0
            },
        }

    for order in orders:
        if order.status == 'initialized':
            order.status = 'pending'
        fees = DataGetter.get_fee_settings_by_currency(DataGetter.get_event(order.event_id).payment_currency)
        orders_summary[str(order.status)]['orders_count'] += 1
        orders_summary[str(order.status)]['total_sales'] += order.amount

        for order_ticket in order.tickets:
            discount = TicketingManager.get_discount_code(event_id, order.discount_code_id)
            orders_summary[str(order.status)]['tickets_count'] += order_ticket.quantity
            ticket = get_ticket(order_ticket.ticket_id)
            tickets_summary[str(ticket.id)][str(order.status)]['tickets_count'] += order_ticket.quantity
            ticket_price = ticket.price
            if fees and not ticket.absorb_fees:
                order_fee = fees.service_fee * (ticket.price * order_ticket.quantity) / 100.0
                if order_fee > fees.maximum_fee:
                    ticket_price = ticket.price + fees.maximum_fee / order_ticket.quantity
                else:
                    ticket_price = ticket.price + fees.service_fee * ticket.price / 100.0

            if order.paid_via != 'free' and order.amount > 0:
                if discount and str(ticket.id) in discount.tickets.split(","):
                    if discount.type == "amount":
                        tickets_summary[str(ticket.id)][str(order.status)]['sales'] += order_ticket.quantity * (
                            ticket_price - discount.value)
                    else:
                        tickets_summary[str(ticket.id)][str(order.status)]['sales'] += order_ticket.quantity * (
                            ticket_price - discount.value * ticket_price / 100.0)
                else:
                    tickets_summary[str(ticket.id)][str(order.status)]['sales'] += order_ticket.quantity * ticket_price
    return render_template('gentelella/users/events/tickets/tickets.html', event=event, event_id=event_id,
                           orders_summary=orders_summary, tickets_summary=tickets_summary)


@event_ticket_sales.route('/orders/')
def display_orders(event_id, pdf=None):
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    discount_code = request.args.get('discount_code')
    if ('from_date' in request.args and not from_date) or ('to_date' in request.args and not to_date) or \
        ('from_date' in request.args and 'to_date' not in request.args) or \
        ('to_date' in request.args and 'from_date' not in request.args):
        return redirect(url_for('.display_orders', event_id=event_id))
    if from_date and to_date:
        orders = TicketingManager.get_orders(
            event_id=event_id,
            from_date=datetime.strptime(from_date, '%d/%m/%Y'),
            to_date=datetime.strptime(to_date, '%d/%m/%Y')
        )
    elif discount_code == '':
        return redirect(url_for('.display_orders', event_id=event_id))
    elif discount_code:
        orders = TicketingManager.get_orders(
            event_id=event_id,
            discount_code=discount_code,
        )
    else:
        orders = TicketingManager.get_orders(event_id)
    event = DataGetter.get_event(event_id)
    if pdf is not None:
        return (event, event_id, orders, discount_code)
    else:
        return render_template('gentelella/users/events/tickets/orders.html', event=event, event_id=event_id,
                               orders=orders, from_date=from_date, to_date=to_date, discount_code=discount_code)


@event_ticket_sales.route('/attendees/')
def display_attendees(event_id, pdf=None):
    event = DataGetter.get_event(event_id)
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    selected_ticket = request.args.get('ticket_name')
    if ('from_date' in request.args and not from_date) or ('to_date' in request.args and not to_date) or \
        ('from_date' in request.args and 'to_date' not in request.args) or \
        ('to_date' in request.args and 'from_date' not in request.args):
        return redirect(url_for('.display_attendees', event_id=event_id))
    if from_date and to_date:
        orders = TicketingManager.get_orders(
            event_id=event_id,
            from_date=datetime.strptime(from_date, '%d/%m/%Y'),
            to_date=datetime.strptime(to_date, '%d/%m/%Y')
        )
    else:
        orders = TicketingManager.get_orders(event_id)
    holders = []
    ticket_names = []
    for ticket in event.tickets:
        ticket_names.append(ticket.name)
    for order in orders:
        for holder in order.ticket_holders:
            if selected_ticket is not None:
                if selected_ticket != "All":
                    if holder.ticket.name != selected_ticket:
                        continue
            discount = TicketingManager.get_discount_code(event_id, order.discount_code_id)
            order_holder = {
                'order_invoice': order.get_invoice_number(),
                'paid_via': order.paid_via,
                'status': order.status,
                'completed_at': order.completed_at,
                'created_at': order.created_at,
                'ticket_name': holder.ticket.name,
                'ticket_type': holder.ticket.type,
                'firstname': holder.firstname,
                'lastname': holder.lastname,
                'email': holder.email,
                'country': holder.country,
                'ticket_price': holder.ticket.price,
                'discount': discount
            }

            if order.status == 'completed':
                order_holder['order_url'] = url_for('ticketing.view_order_after_payment',
                                                    order_identifier=order.identifier)
            else:
                order_holder['order_url'] = url_for('ticketing.show_transaction_error',
                                                    order_identifier=order.identifier)

            order_holder['by_whom'] = order.user.user_detail.fullname \
                if order.user.user_detail and order.user.user_detail.fullname else order.user.email
            if discount and str(holder.ticket.id) in discount.tickets.split(","):
                if discount.type == "amount":
                    order_holder['ticket_price'] = order_holder['ticket_price'] - discount.value
                else:
                    order_holder['ticket_price'] -= order_holder['ticket_price'] * discount.value / 100.0
            order_holder['checked_in'] = holder.checked_in
            order_holder['id'] = holder.id
            holders.append(order_holder)
        if len(order.ticket_holders) == 0:

            order_holder = {
                'order_invoice': order.get_invoice_number(),
                'paid_via': order.paid_via,
                'status': order.status,
                'completed_at': order.completed_at,
                'created_at': order.created_at
            }

            if order.status == 'completed':
                order_holder['order_url'] = url_for('ticketing.view_order_after_payment',
                                                    order_identifier=order.identifier)
            else:
                order_holder['order_url'] = url_for('ticketing.show_transaction_error',
                                                    order_identifier=order.identifier)

            order_holder['by_whom'] = order.user.user_detail.fullname \
                if order.user.user_detail and order.user.user_detail.fullname else order.user.email

            holders.append(order_holder)

    if pdf is not None:
        return (event, event_id, holders, orders, ticket_names, selected_ticket)
    else:
        return render_template('gentelella/users/events/tickets/attendees.html', event=event,
                               event_id=event_id, holders=holders, from_date=from_date, to_date=to_date,
                               ticket_names=ticket_names, selected_ticket=selected_ticket)


@event_ticket_sales.route('/attendees/pdf')
def download_as_pdf(event_id):
    (event, event_id, holders, orders, ticket_names, selected_ticket) = display_attendees(event_id, pdf='print_pdf')
    pdf = create_pdf(render_template('gentelella/users/events/tickets/download_attendees.html', event=event,
                                     event_id=event_id, holders=holders, ticket_names=ticket_names,
                                     selected_ticket=selected_ticket))
    response = make_response(pdf.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = \
        'inline; filename=%s.csv' % (re.sub(r"[^\w\s]", '', event.name).replace(" ", "_"))
    return response


@event_ticket_sales.route('/attendees/csv')
def download_as_csv(event_id):
    (event, event_id, holders, orders, ticket_names, selected_ticket) = display_attendees(event_id, pdf='print_csv')
    value = 'Order#,Order Date, Status, First Name, Last Name, Email, Country,' \
            'Payment Type, Ticket Name, Ticket Price, Ticket Type \n'

    for holder in holders:
        if holder['status'] != "deleted":
            if 'order_invoice' in holder:
                value += holder['order_invoice']
            value += ','
            if 'created_at' in holder:
                value += str(holder['created_at'])
            value += ','
            if 'status' in holder:
                value += holder['status']
            value += ','
            if 'firstname' in holder:
                value += holder['firstname']
            value += ','
            if 'lastname' in holder:
                value += holder['lastname']
            value += ','
            if 'email' in holder:
                value += holder['email']
            value += ','
            if 'country' in holder:
                value += str(holder['country'])
            value += ','
            if 'paid_via' in holder and holder['paid_via']:
                value += holder['paid_via']
            value += ','
            if 'ticket_name' in holder:
                value += str(holder['ticket_name'])
            value += ','
            if 'ticket_price' in holder:
                value += str(holder['ticket_price'])
            value += ','
            if 'ticket_type' in holder:
                value += str(holder['ticket_type'])
            value += ','
            value += '\n'

    response = make_response(value)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = \
        'inline; filename=%s.csv' % (re.sub(r"[^\w\s]", '', event.name).replace(" ", "_"))

    return response


@event_ticket_sales.route('/orders/pdf')
def download_orders_as_pdf(event_id):
    (event, event_id, orders, discount_code) = display_orders(event_id, pdf='print_pdf')
    pdf = create_pdf(render_template('gentelella/users/events/tickets/download_orders.html', event=event, event_id=event_id,
                                     orders=orders, discount_code=discount_code))
    response = make_response(pdf.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = \
        'inline; filename=%s.csv' % (re.sub(r"[^\w\s]", '', event.name).replace(" ", "_"))
    return response


@event_ticket_sales.route('/orders/csv')
def download_orders_as_csv(event_id):
    (event, event_id, holders, orders, ticket_names, selected_ticket) = display_attendees(event_id, pdf='print_csv')
    value = 'Order#,Order Date, Status, Payment Type, Quantity,Total Amount,Discount Code,' \
            'First Name, Last Name, Email \n'

    for order in orders:
        if order.status != "deleted":
            # To avoid KeyError exception
            try:
                value += str(order.get_invoice_number()) + ','
            except:
                value += ','
            try:
                value += str(order.created_at) + ','
            except:
                value += ','
            try:
                value += order.status + ','
            except:
                value += ','
            try:
                value += order.paid_via + ','
            except:
                value += ','
            try:
                value += str(order.get_tickets_count()) + ','
            except:
                value += ','
            try:
                value += str(order.amount) + ','
            except:
                value += ','
            try:
                value += order.discount_code.code + ','
            except:
                value += ','
            try:
                value += order.user.user_detail.firstname + ','
            except:
                value += ','
            try:
                value += order.user.user_detail.lastname + ','
            except:
                value += ','
            try:
                value += order.user.email + ','
            except:
                value += ','
            value += '\n'

    response = make_response(value)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = \
        'inline; filename=%s.csv' % (re.sub(r"[^\w\s]", '', event.name).replace(" ", "_"))

    return response


@event_ticket_sales.route('/add-order/', methods=('GET', 'POST'))
def add_order(event_id):
    if request.method == 'POST':
        order = TicketingManager.create_order(request.form, True)
        return redirect(url_for('.proceed_order', event_id=event_id, order_identifier=order.identifier))

    event = DataGetter.get_event(event_id)
    return render_template('gentelella/users/events/tickets/add_order.html', event=event, event_id=event_id)


@event_ticket_sales.route('/<order_identifier>/')
def proceed_order(event_id, order_identifier):
    order = TicketingManager.get_order_by_identifier(order_identifier)
    if order:
        if order.status == 'completed':
            return redirect(url_for('ticketing.view_order_after_payment', order_identifier=order_identifier))
        return render_template('gentelella/guest/ticketing/order_pre_payment.html', order=order, event=order.event,
                               countries=list(pycountry.countries),
                               from_organizer=True,
                               pay_via=order.paid_via,
                               stripe_publishable_key=get_settings()['stripe_publishable_key'])
    else:
        abort(404)
    return redirect(url_for('.display_ticket_stats', event_id=event_id))


@event_ticket_sales.route('/discounts/')
def discount_codes_view(event_id):
    event = DataGetter.get_event(event_id)
    discount_codes = TicketingManager.get_discount_codes(event_id)
    return render_template('gentelella/users/events/tickets/discount_codes.html', event=event,
                           discount_codes=discount_codes,
                           event_id=event_id)


@event_ticket_sales.route('/discounts/create/', methods=('GET', 'POST'))
def discount_codes_create(event_id, discount_code_id=None):
    event = DataGetter.get_event(event_id)
    if request.method == 'POST':
        TicketingManager.create_edit_discount_code(request.form, event_id)
        flash("The discount code has been added.", "success")
        return redirect(url_for('.discount_codes_view', event_id=event_id))
    discount_code = None
    if discount_code_id:
        discount_code = TicketingManager.get_discount_code(event_id, discount_code_id)
    return render_template('gentelella/users/events/tickets/discount_codes_create.html', event=event, event_id=event_id,
                           discount_code=discount_code)


@event_ticket_sales.route('/discounts/check/duplicate/')
def check_duplicate_discount_code(event_id):
    code = request.args.get('code')
    current = request.args.get('current')
    if not current:
        current = ''
    discount_code = TicketingManager.get_discount_code(event_id, code)
    if (current == "" and discount_code) or (current != "" and discount_code and discount_code.id != int(current)):
        return jsonify({
            "status": "invalid"
        }), 404

    return jsonify({
        "status": "valid"
    }), 200


@event_ticket_sales.route('/discounts/<int:discount_code_id>/edit/', methods=('GET', 'POST'))
def discount_codes_edit(event_id, discount_code_id=None):
    if not TicketingManager.get_discount_code(event_id, discount_code_id):
        abort(404)
    if request.method == 'POST':
        TicketingManager.create_edit_discount_code(request.form, event_id, discount_code_id)
        flash("The discount code has been edited.", "success")
        return redirect(url_for('.discount_codes_view', event_id=event_id))
    return discount_codes_create(event_id, discount_code_id)


@event_ticket_sales.route('/discounts/<int:discount_code_id>/toggle/')
def discount_codes_toggle(event_id, discount_code_id=None):
    discount_code = TicketingManager.get_discount_code(event_id, discount_code_id)
    if not discount_code:
        abort(404)
    discount_code.is_active = not discount_code.is_active
    save_to_db(discount_code)
    message = "Activated." if discount_code.is_active else "Deactivated."
    flash("The discount code has been " + message, "success")
    return redirect(url_for('.discount_codes_view', event_id=event_id))


@event_ticket_sales.route('/discounts/<int:discount_code_id>/delete/')
def discount_codes_delete(event_id, discount_code_id=None):
    discount_code = TicketingManager.get_discount_code(event_id, discount_code_id)
    if not discount_code:
        abort(404)
    delete_from_db(discount_code, "Discount code deleted")
    flash("The discount code has been deleted.", "warning")
    return redirect(url_for('.discount_codes_view', event_id=event_id))


@event_ticket_sales.route('/access/')
def access_codes_view(event_id):
    event = DataGetter.get_event(event_id)
    access_codes = TicketingManager.get_access_codes(event_id)
    return render_template('gentelella/users/events/tickets/access_codes.html', event=event,
                           access_codes=access_codes,
                           event_id=event_id)


@event_ticket_sales.route('/access/create/', methods=('GET', 'POST'))
def access_codes_create(event_id, access_code_id=None):
    event = DataGetter.get_event(event_id)
    if request.method == 'POST':
        TicketingManager.create_edit_access_code(request.form, event_id)
        flash("The access code has been added.", "success")
        return redirect(url_for('.access_codes_view', event_id=event_id))
    access_code = None
    if access_code_id:
        access_code = TicketingManager.get_access_code(event_id, access_code_id)
    return render_template('gentelella/users/events/tickets/access_codes_create.html', event=event, event_id=event_id,
                           access_code=access_code)


@event_ticket_sales.route('/access/check/duplicate/')
def check_duplicate_access_code(event_id):
    code = request.args.get('code')
    current = request.args.get('current')
    if not current:
        current = ''
    access_code = TicketingManager.get_access_code(event_id, code)
    if (current == "" and access_code) or (current != "" and access_code and access_code.id != int(current)):
        return jsonify({
            "status": "invalid"
        }), 404

    return jsonify({
        "status": "valid"
    }), 200


@event_ticket_sales.route('/access/<int:access_code_id>/edit/', methods=('GET', 'POST'))
def access_codes_edit(event_id, access_code_id=None):
    if not TicketingManager.get_access_code(event_id, access_code_id):
        abort(404)
    if request.method == 'POST':
        TicketingManager.create_edit_access_code(request.form, event_id, access_code_id)
        flash("The access code has been edited.", "success")
        return redirect(url_for('.access_codes_view', event_id=event_id))
    return access_codes_create(event_id, access_code_id)


@event_ticket_sales.route('/access/<int:access_code_id>/toggle/')
def access_codes_toggle(event_id, access_code_id=None):
    access_code = TicketingManager.get_access_code(event_id, access_code_id)
    if not access_code:
        abort(404)
    access_code.is_active = not access_code.is_active
    save_to_db(access_code)
    message = "Activated." if access_code.is_active else "Deactivated."
    flash("The access code has been " + message, "success")
    return redirect(url_for('.access_codes_view', event_id=event_id))


@event_ticket_sales.route('/access/<int:access_code_id>/delete/')
def access_codes_delete(event_id, access_code_id=None):
    access_code = TicketingManager.get_access_code(event_id, access_code_id)
    if not access_code:
        abort(404)
    delete_from_db(access_code, "Access code deleted")
    flash("The access code has been deleted.", "warning")
    return redirect(url_for('.access_codes_view', event_id=event_id))


@event_ticket_sales.route('/attendees/check_in_toggle/<holder_id>/', methods=('POST',))
def attendee_check_in_toggle(event_id, holder_id):
    holder = TicketingManager.attendee_check_in_out(event_id, holder_id)
    if holder:
        return jsonify({
            'status': 'ok',
            'checked_in': holder.checked_in
        })

    return jsonify({
        'status': 'invalid_holder_id'
    })


@event_ticket_sales.route('/cancel/', methods=('POST',))
def cancel_order(event_id):
    return_status = TicketingManager.cancel_order(request.form)
    if return_status:
        return redirect(url_for('.display_orders', event_id=event_id))
    else:
        abort(403)


@event_ticket_sales.route('/delete/', methods=('POST',))
def delete_order(event_id):
    return_status = TicketingManager.delete_order(request.form)
    if return_status:
        return redirect(url_for('.display_orders', event_id=event_id))
    else:
        abort(403)


@event_ticket_sales.route('/resend-confirmation/', methods=('POST',))
def resend_confirmation(event_id):
    return_status = TicketingManager.resend_confirmation(request.form)
    if return_status:
        return redirect(url_for('.display_orders', event_id=event_id))
    else:
        abort(403)
