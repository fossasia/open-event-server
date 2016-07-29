from flask.ext.restplus import abort
from flask_admin import BaseView, expose
from flask import redirect, url_for, request, jsonify

import pycountry

from app import get_settings
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
        if not order or order.status == 'expired':
            abort(404)
        if order.state == 'completed':
            return redirect(url_for('.view_order_after_payment', order_identifier=order_identifier))
        return self.render('/gentelella/guest/ticketing/order_pre_payment.html', order=order, event=order.event,
                           countries=list(pycountry.countries),
                           stripe_publishable_key=get_settings()['stripe_publishable_key'])

    @expose('/<order_identifier>/view/', methods=('GET',))
    def view_order_after_payment(self, order_identifier):
        order = TicketingManager.get_and_set_expiry(order_identifier)
        if not order or order.status != 'completed':
            abort(404)
        return self.render('/gentelella/guest/ticketing/order_post_payment.html', order=order, event=order.event)

    @expose('/initiate/payment/', methods=('POST',))
    def initiate_order_payment(self):
        result = TicketingManager.initiate_order_payment(request.form)
        if result:
            return jsonify({
                "status": "ok",
                "email": result.user.email
            })
        else:
            return jsonify({
                "status": "error"
            })

    @expose('/charge/payment/', methods=('POST',))
    def charge_order_payment(self):
        result = TicketingManager.charge_order_payment(request.form)
        if result:
            return jsonify({
                "status": "ok",
                "order": result
            })
        else:
            return jsonify({
                "status": "error"
            })

    @expose('/expire/<order_identifier>/', methods=('POST',))
    def expire_order(self, order_identifier):
        TicketingManager.get_and_set_expiry(order_identifier)
        return jsonify({
            "status": "ok"
        })
