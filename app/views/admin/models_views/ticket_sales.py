import flask_login
import pycountry
from flask import abort, jsonify
from flask import redirect, flash
from flask import request
from flask import url_for
from flask_admin import BaseView, expose

from app.helpers.data import delete_from_db
from app import get_settings
from app.helpers.cache import cache
from app.helpers.data import save_to_db
from app.helpers.data_getter import DataGetter
from app.helpers.ticketing import TicketingManager
from app.models.ticket import Ticket


class TicketSalesView(BaseView):
    @cache.memoize(50)
    def get_ticket(self, ticket_id):
        return Ticket.query.get(ticket_id)

    @expose('/')
    @flask_login.login_required
    def display_ticket_stats(self, event_id):
        event = DataGetter.get_event(event_id)
        orders = TicketingManager.get_orders(event_id)

        completed_count = 0
        completed_amount = 0
        tickets_count = 0

        orders_summary = {
            'completed': {
                'class': 'success',
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
                ticket = self.get_ticket(order_ticket.ticket_id)
                tickets_summary[str(ticket.id)][str(order.status)]['tickets_count'] += order_ticket.quantity
                if order.paid_via != 'free' and order.amount > 0:
                    tickets_summary[str(ticket.id)][str(order.status)]['sales'] += order_ticket.quantity * ticket.price

        return self.render('/gentelella/admin/event/tickets/tickets.html', event=event, event_id=event_id,
                           orders_summary=orders_summary, tickets_summary=tickets_summary)

    @expose('/orders/')
    @flask_login.login_required
    def display_orders(self, event_id):
        event = DataGetter.get_event(event_id)
        orders = TicketingManager.get_orders(event_id)
        return self.render('/gentelella/admin/event/tickets/orders.html', event=event, event_id=event_id, orders=orders)

    @expose('/attendees/')
    @flask_login.login_required
    def display_attendees(self, event_id):
        event = DataGetter.get_event(event_id)
        orders = TicketingManager.get_orders(event_id, status='completed')
        return self.render('/gentelella/admin/event/tickets/attendees.html', event=event,
                           event_id=event_id, orders=orders)

    @expose('/add-order/', methods=('GET', 'POST'))
    @flask_login.login_required
    def add_order(self, event_id):

        if request.method == 'POST':
            order = TicketingManager.create_order(request.form, True)
            return redirect(url_for('.proceed_order', event_id=event_id, order_identifier=order.identifier))

        event = DataGetter.get_event(event_id)
        return self.render('/gentelella/admin/event/tickets/add_order.html', event=event, event_id=event_id)

    @expose('/<order_identifier>/', methods=('GET',))
    def proceed_order(self, event_id, order_identifier):
        order = TicketingManager.get_order_by_identifier(order_identifier)
        if order:
            if order.status == 'completed':
                return redirect(url_for('ticketing.view_order_after_payment', order_identifier=order_identifier))
            return self.render('/gentelella/guest/ticketing/order_pre_payment.html', order=order, event=order.event,
                               countries=list(pycountry.countries),
                               from_organizer=True,
                               pay_via=order.paid_via,
                               stripe_publishable_key=get_settings()['stripe_publishable_key'])
        else:
            abort(404)
        return redirect(url_for('.display_ticket_stats', event_id=event_id))

    @expose('/discounts/', methods=('GET',))
    @flask_login.login_required
    def discount_codes_view(self, event_id):
        event = DataGetter.get_event(event_id)
        discount_codes = TicketingManager.get_discount_codes(event_id)
        return self.render('/gentelella/admin/event/tickets/discount_codes.html', event=event,
                           discount_codes=discount_codes,
                           event_id=event_id)

    @expose('/discounts/create/', methods=('GET', 'POST'))
    @flask_login.login_required
    def discount_codes_create(self, event_id, discount_code_id=None):
        event = DataGetter.get_event(event_id)
        if request.method == 'POST':
            TicketingManager.create_edit_discount_code(request.form, event_id)
            flash("The discount code has been added.", "success")
            return redirect(url_for('.discount_codes_view', event_id=event_id))
        discount_code = None
        if discount_code_id:
            discount_code = TicketingManager.get_discount_code(event_id, discount_code_id)
        return self.render('/gentelella/admin/event/tickets/discount_codes_create.html', event=event, event_id=event_id,
                           discount_code=discount_code)

    @expose('/discounts/check/duplicate/', methods=('GET',))
    @flask_login.login_required
    def check_duplicate_discount_code(self, event_id):
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

    @expose('/discounts/<int:discount_code_id>/edit/', methods=('GET', 'POST'))
    @flask_login.login_required
    def discount_codes_edit(self, event_id, discount_code_id=None):
        if not TicketingManager.get_discount_code(event_id, discount_code_id):
            abort(404)
        if request.method == 'POST':
            TicketingManager.create_edit_discount_code(request.form, event_id, discount_code_id)
            flash("The discount code has been edited.", "success")
            return redirect(url_for('.discount_codes_view', event_id=event_id))
        return self.discount_codes_create(event_id, discount_code_id)

    @expose('/discounts/<int:discount_code_id>/toggle/', methods=('GET',))
    @flask_login.login_required
    def discount_codes_toggle(self, event_id, discount_code_id=None):
        discount_code = TicketingManager.get_discount_code(event_id, discount_code_id)
        if not discount_code:
            abort(404)
        discount_code.is_active = not discount_code.is_active
        save_to_db(discount_code)
        message = "Activated." if discount_code.is_active else "Deactivated."
        flash("The discount code has been " + message, "success")
        return redirect(url_for('.discount_codes_view', event_id=event_id))

    @expose('/discounts/<int:discount_code_id>/delete/', methods=('GET',))
    @flask_login.login_required
    def discount_codes_delete(self, event_id, discount_code_id=None):
        discount_code = TicketingManager.get_discount_code(event_id, discount_code_id)
        if not discount_code:
            abort(404)
        delete_from_db(discount_code, "Discount code deleted")
        flash("The discount code has been deleted.", "warning")
        return redirect(url_for('.discount_codes_view', event_id=event_id))

    @expose('/attendees/check_in_toggle/<holder_id>/', methods=('POST',))
    @flask_login.login_required
    def attendee_check_in_toggle(self, event_id, holder_id):
        holder = TicketingManager.attendee_check_in_out(holder_id)
        if holder:
            return jsonify({
                'status': 'ok',
                'checked_in': holder.checked_in
            })

        return jsonify({
            'status': 'invalid_holder_id'
        })
