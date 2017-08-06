from flask_rest_jsonapi.data_layers.base import BaseDataLayer

from app.api.helpers.exceptions import UnprocessableEntity
from app.api.helpers.ticketing import TicketingManager
from app.models.order import Order


class ChargesLayer(BaseDataLayer):

    def create_object(self, data, view_kwargs):
        order = Order.query.filter_by(id=view_kwargs['id']).first()
        if order.payment_mode == 'stripe':
            if data.get('stripe') is None:
                raise UnprocessableEntity({'source': ''}, "stripe token is missing")
            success, response = TicketingManager.charge_stripe_order_payment(order, data['stripe'])
            if not success:
                raise UnprocessableEntity({'source': 'stripe_token_id'}, response)

        elif order.payment_mode == 'paypal':
            success, response = TicketingManager.charge_paypal_order_payment(order)
            if not success:
                raise UnprocessableEntity({'source': ''}, response)
        return order
