import flask_login
from flask_admin import BaseView, expose
from app.helpers.ticketing import TicketingManager


class MyTicketsView(BaseView):

    @expose('/')
    @flask_login.login_required
    def display_my_tickets(self):
        page_content = {"tab_upcoming_events": "Upcoming Events",
                        "tab_past_events": "Past Events",
                        "title": "My Tickets"}

        upcoming_events_orders = TicketingManager.get_orders_of_user(upcoming_events=True)
        past_events_orders = TicketingManager.get_orders_of_user(upcoming_events=False)
        placeholder_images = DataGetter.get_event_default_images()

        return self.render('/gentelella/admin/mytickets/mytickets_list.html',
                           page_content=page_content,
                           upcoming_events_orders=upcoming_events_orders,
                           past_events_orders=past_events_orders,
                           placeholder_images=placeholder_images)
