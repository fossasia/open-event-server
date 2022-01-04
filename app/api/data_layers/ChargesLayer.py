from flask_rest_jsonapi.data_layers.base import BaseDataLayer
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.helpers.errors import ConflictError, UnprocessableEntityError
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

        if view_kwargs.get('order_identifier').isdigit():
            # when id is passed
            order = Order.query.filter_by(id=view_kwargs['order_identifier']).first()
        else:
            # when identifier is passed
            order = Order.query.filter_by(
                identifier=view_kwargs['order_identifier']
            ).first()

        if not order:
            raise ObjectNotFound(
                {'parameter': 'order_identifier'},
                "Order with identifier: {} not found".format(
                    view_kwargs['order_identifier']
                ),
            )
        if (
            order.status == 'cancelled'
            or order.status == 'expired'
            or order.status == 'completed'
        ):
            raise ConflictError(
                {'parameter': 'id'},
                "You cannot charge payments on a cancelled, expired or completed order",
            )
        if (not order.amount) or order.amount == 0:
            raise ConflictError(
                {'parameter': 'id'}, "You cannot charge payments on a free order"
            )

        data['id'] = order.id

        # charge through stripe
        if order.payment_mode == 'stripe':
            if not order.event.can_pay_by_stripe:
                raise ConflictError(
                    {'': ''}, "This event doesn't accept payments by Stripe"
                )

            success, response = TicketingManager.create_payment_intent_for_order_stripe(
                order
            )
            data['status'] = success
            data['message'] = response

        # charge through paypal
        elif order.payment_mode == 'paypal':
            if (not data.get('paypal_payer_id')) or (not data.get('paypal_payment_id')):
                raise UnprocessableEntityError(
                    {'source': ''}, "paypal_payer_id or paypal_payment_id or both missing"
                )
            if not order.event.can_pay_by_paypal:
                raise ConflictError(
                    {'': ''}, "This event doesn't accept payments by Paypal"
                )

            success, response = TicketingManager.charge_paypal_order_payment(
                order, data['paypal_payer_id'], data['paypal_payment_id']
            )
            data['status'] = success
            data['message'] = response

        return data
