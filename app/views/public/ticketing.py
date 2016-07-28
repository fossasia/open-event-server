from flask_admin import BaseView, expose
from flask import redirect, url_for, request

from app.helpers.ticketing import TicketingManager
from app.helpers.data_getter import DataGetter

class TicketingView(BaseView):
    @expose('/', methods=('GET', 'POST'))
    def index(self):
        pass

    @expose('/create', methods=('POST', ))
    def create_order(self):
        order = TicketingManager.create_order(request.form)
        return redirect(url_for('.view_order', order_identifier=order.identifier))

    @expose('/<order_identifier>', methods=('GET',))
    def view_order(self, order_identifier):
        order = TicketingManager.get_order_by_identifier(order_identifier)
        return self.render('/gentelella/guest/ticketing/summary.html', order=order, event=order.event)

