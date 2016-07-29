from flask.ext.restplus import abort
from flask_admin import BaseView, expose
from flask import redirect, url_for, request, jsonify

from app.helpers.ticketing import TicketingManager

class TicketingView(BaseView):
    @expose('/', methods=('GET', 'POST'))
    def index(self):
        pass

    @expose('/create/', methods=('POST', ))
    def create_order(self):
        order = TicketingManager.create_order(request.form)
        return redirect(url_for('.view_order', order_identifier=order.identifier))

    @expose('/<order_identifier>/', methods=('GET',))
    def view_order(self, order_identifier):
        order = TicketingManager.get_and_set_expiry(order_identifier)
        if not order or order.state == 'expired':
            abort(404)
        return self.render('/gentelella/guest/ticketing/summary.html', order=order, event=order.event)

    @expose('/expire/<order_identifier>/', methods=('POST',))
    def expire_order(self, order_identifier):
        TicketingManager.get_and_set_expiry(order_identifier)
        return jsonify({
            "status": "ok"
        })
