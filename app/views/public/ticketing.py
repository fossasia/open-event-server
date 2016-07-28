from flask_admin import BaseView, expose
from app.models.order import Order
from app.models.ticket_holder import TicketHolder
from app.helpers.ticketing import TicketingManager

class TicketingView(BaseView):
    @expose('/', methods=('GET', 'POST'))
    def index(self):
        pass

    @expose('/create', methods=('POST', ))
    def create_order(self, url):
        return self.render('/gentelella/guest/page.html')

    @expose('/<order_identifier>', methods=('GET',))
    def view_order(self, order_identifier):
        return self.render('/gentelella/guest/page.html')

