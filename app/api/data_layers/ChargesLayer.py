from flask_rest_jsonapi.data_layers.base import BaseDataLayer
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.helpers.exceptions import UnprocessableEntity, ConflictException
from app.api.helpers.ticketing import TicketingManager
from app.models.order import Order


class ChargesLayer(BaseDataLayer):

    def create_object(self, data, view_kwargs):
        """
        create_object method for the Charges layer
        charge the user using paypal or stripe
        :param data:
        :param view_kwargs:
        :return:
        """
        order = Order.query.filter_by(id=view_kwargs['id']).first()
        if not order:
            raise ObjectNotFound({'parameter': 'id'},
                                 "Order with id: {} not found".format(view_kwargs['id']))
        elif order.status == 'cancelled' or order.status == 'expired' or order.status == 'completed':
            raise ConflictException({'parameter': 'id'},
                                    "You cannot charge payments on a cancelled, expired or completed order")
        elif (not order.amount) or order.amount == 0:
            raise ConflictException({'parameter': 'id'},
                                    "You cannot charge payments on a free order")

        # charge through stripe
        if order.payment_mode == 'stripe':
            if not data.get('stripe'):
                raise UnprocessableEntity({'source': ''}, "stripe token is missing")
            success, response = TicketingManager.charge_stripe_order_payment(order, data['stripe'])
            if not success:
                raise UnprocessableEntity({'source': 'stripe_token_id'}, response)

        # charge through paypal
        elif order.payment_mode == 'paypal':
            if not data.get('paypal'):
                raise UnprocessableEntity({'source': ''}, "paypal token is missing")
            success, response = TicketingManager.charge_paypal_order_payment(order, data['paypal'])
            if not success:
                raise UnprocessableEntity({'source': 'paypal'}, response)
        return order
