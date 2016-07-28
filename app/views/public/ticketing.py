from flask_admin import BaseView, expose
from flask import redirect, url_for

from app.models.order import Order
from app.models.ticket_holder import TicketHolder
from app.helpers.ticketing import TicketingManager

class TicketingView(BaseView):
    @expose('/', methods=('GET', 'POST'))
    def index(self):
        pass

    @expose('/create', methods=('POST', ))
    def create_order(self):
        return redirect(url_for('.view_order', order_identifier='abc'))

    @expose('/<order_identifier>', methods=('GET',))
    def view_order(self, order_identifier):
        return self.render('/gentelella/guest/ticketing/summary.html')

