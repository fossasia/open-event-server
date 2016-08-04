import flask_login
import pycountry
from flask import redirect, flash
from flask import request
from flask import url_for
from flask_admin import BaseView, expose

from app import get_settings
from app.helpers.cache import cache
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
        orders = TicketingManager.get_orders(event_id)
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
            if self.is_order_completed(order):
                return redirect(url_for('ticketing.view_order_after_payment', order_identifier=order_identifier))
            return self.render('/gentelella/guest/ticketing/order_pre_payment.html', order=order, event=order.event,
                               countries=list(pycountry.countries),
                               from_organizer=True,
                               pay_via=order.paid_via,
                               stripe_publishable_key=get_settings()['stripe_publishable_key'])
        flash("Can't find order", 'warning')
        return redirect(url_for('.display_ticket_stats', event_id=event_id))

    @staticmethod
    def is_order_completed(order):
        return order.status == 'completed'
