import pycountry
from flask import Blueprint
from flask import abort, jsonify
from flask import redirect, flash
from flask import request, render_template
from flask import url_for

from app import get_settings
from app.helpers.cache import cache
from app.helpers.data import delete_from_db
from app.helpers.data import save_to_db
from app.helpers.data_getter import DataGetter
from app.helpers.ticketing import TicketingManager
from app.models.ticket import Ticket

event_ticket_sales = Blueprint('event_ticket_sales', __name__, url_prefix='/events/<int:event_id>/tickets')


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
            }
        }

    for order in orders:
        if order.status == 'initialized':
            order.status = 'pending'
        orders_summary[str(order.status)]['orders_count'] += 1
        orders_summary[str(order.status)]['total_sales'] += order.amount
        for order_ticket in order.tickets:
            orders_summary[str(order.status)]['tickets_count'] += order_ticket.quantity
            ticket = get_ticket(order_ticket.ticket_id)
            tickets_summary[str(ticket.id)][str(order.status)]['tickets_count'] += order_ticket.quantity
            if order.paid_via != 'free' and order.amount > 0:
                tickets_summary[str(ticket.id)][str(order.status)]['sales'] += order_ticket.quantity * ticket.price

    return render_template('gentelella/admin/event/tickets/tickets.html', event=event, event_id=event_id,
                           orders_summary=orders_summary, tickets_summary=tickets_summary)


@event_ticket_sales.route('/orders/')
def display_orders(event_id):
    event = DataGetter.get_event(event_id)
    orders = TicketingManager.get_orders(event_id)
    return render_template('gentelella/admin/event/tickets/orders.html', event=event, event_id=event_id, orders=orders)


@event_ticket_sales.route('/attendees/')
def display_attendees(event_id):
    event = DataGetter.get_event(event_id)
    orders = TicketingManager.get_orders(event_id, status='completed')
    return render_template('gentelella/admin/event/tickets/attendees.html', event=event,
                           event_id=event_id, orders=orders)


@event_ticket_sales.route('/add-order/', methods=('GET', 'POST'))
def add_order(event_id):
    if request.method == 'POST':
        order = TicketingManager.create_order(request.form, True)
        return redirect(url_for('.proceed_order', event_id=event_id, order_identifier=order.identifier))

    event = DataGetter.get_event(event_id)
    return render_template('gentelella/admin/event/tickets/add_order.html', event=event, event_id=event_id)


@event_ticket_sales.route('/<order_identifier>/', methods=('GET',))
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


@event_ticket_sales.route('/discounts/', methods=('GET',))
def discount_codes_view(event_id):
    event = DataGetter.get_event(event_id)
    discount_codes = TicketingManager.get_discount_codes(event_id)
    return render_template('gentelella/admin/event/tickets/discount_codes.html', event=event,
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
    return render_template('gentelella/admin/event/tickets/discount_codes_create.html', event=event, event_id=event_id,
                           discount_code=discount_code)


@event_ticket_sales.route('/discounts/check/duplicate/', methods=('GET',))
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


@event_ticket_sales.route('/discounts/<int:discount_code_id>/toggle/', methods=('GET',))
def discount_codes_toggle(event_id, discount_code_id=None):
    discount_code = TicketingManager.get_discount_code(event_id, discount_code_id)
    if not discount_code:
        abort(404)
    discount_code.is_active = not discount_code.is_active
    save_to_db(discount_code)
    message = "Activated." if discount_code.is_active else "Deactivated."
    flash("The discount code has been " + message, "success")
    return redirect(url_for('.discount_codes_view', event_id=event_id))


@event_ticket_sales.route('/discounts/<int:discount_code_id>/delete/', methods=('GET',))
def discount_codes_delete(event_id, discount_code_id=None):
    discount_code = TicketingManager.get_discount_code(event_id, discount_code_id)
    if not discount_code:
        abort(404)
    delete_from_db(discount_code, "Discount code deleted")
    flash("The discount code has been deleted.", "warning")
    return redirect(url_for('.discount_codes_view', event_id=event_id))


@event_ticket_sales.route('/attendees/check_in_toggle/<holder_id>/', methods=('POST',))
def attendee_check_in_toggle(event_id, holder_id):
    holder = TicketingManager.attendee_check_in_out(holder_id)
    if holder:
        return jsonify({
            'status': 'ok',
            'checked_in': holder.checked_in
        })

    return jsonify({
        'status': 'invalid_holder_id'
    })
