import flask_login
from flask_admin import BaseView, expose

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
            orders_summary[str(order.status)]['orders_count'] += 1
            orders_summary[str(order.status)]['total_sales'] += order.amount
            for order_ticket in order.tickets:
                orders_summary[str(order.status)]['tickets_count'] += order_ticket.quantity
                ticket = self.get_ticket(order_ticket.ticket_id)
                tickets_summary[str(ticket.id)][str(order.status)]['tickets_count'] += order_ticket.quantity
                tickets_summary[str(ticket.id)][str(order.status)]['sales'] += order_ticket.quantity * ticket.price

        return self.render('/gentelella/admin/event/tickets/tickets.html', event=event, event_id=event_id,
                           orders_summary=orders_summary, tickets_summary=tickets_summary)
