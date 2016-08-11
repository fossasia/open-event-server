from flask_admin import expose

from app import forex
from app.helpers.data_getter import DataGetter
from app.helpers.ticketing import TicketingManager
from app.models.ticket import Ticket
from app.views.admin.super_admin.super_admin_base import SuperAdminBaseView
from app.helpers.cache import cache

class SuperAdminSalesView(SuperAdminBaseView):

    display_currency = 'USD'

    @cache.memoize(50)
    def get_ticket(self, ticket_id):
        return Ticket.query.get(ticket_id)

    @expose('/')
    def sales_by_events_view(self):
        events = DataGetter.get_all_events()
        orders = TicketingManager.get_orders()

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
        for event in events:
            tickets_summary[str(event.id)] = {
                'name': event.name,
                'payment_currency': event.payment_currency,
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
            orders_summary[str(order.status)]['total_sales'] += forex(order.event.payment_currency,
                                                                      self.display_currency, order.amount)
            for order_ticket in order.tickets:
                orders_summary[str(order.status)]['tickets_count'] += order_ticket.quantity
                ticket = self.get_ticket(order_ticket.ticket_id)
                tickets_summary[str(order.event_id)][str(order.status)]['tickets_count'] += order_ticket.quantity
                if order.paid_via != 'free' and order.amount > 0:
                    tickets_summary[str(order.event_id)][str(order.status)]['sales'] += order_ticket.quantity \
                                                                                        * ticket.price

        return self.render('/gentelella/admin/super_admin/sales/by_events.html',
                           tickets_summary=tickets_summary,
                           display_currency=self.display_currency,
                           orders_summary=orders_summary)
