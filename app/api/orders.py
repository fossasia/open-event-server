import json
import logging
import time

import omise
import requests
from flask import Blueprint, current_app, jsonify, redirect, request, url_for
from flask_jwt_extended import current_user
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from app.api.bootstrap import api
from app.api.data_layers.ChargesLayer import ChargesLayer
from app.api.helpers.custom_forms import validate_custom_form_constraints_request
from app.api.helpers.db import safe_query, safe_query_by_id, safe_query_kwargs, save_to_db
from app.api.helpers.errors import (
    BadRequestError,
    ConflictError,
    ForbiddenError,
    UnprocessableEntityError,
)
from app.api.helpers.files import make_frontend_url
from app.api.helpers.mail import send_order_cancel_email
from app.api.helpers.notification import notify_ticket_cancel
from app.api.helpers.order import (
    create_onsite_attendees_for_order,
    delete_related_attendees_for_order,
    on_order_completed,
)
from app.api.helpers.payment import (
    AliPayPaymentsManager,
    OmisePaymentsManager,
    PayPalPaymentsManager,
    PaytmPaymentsManager,
)
from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required
from app.api.helpers.query import event_query
from app.api.helpers.ticketing import validate_discount_code, validate_ticket_holders
from app.api.helpers.utilities import dasherize, require_relationship
from app.api.schema.attendees import AttendeeSchema
from app.api.schema.orders import OrderSchema
from app.models import db
from app.models.order import Order, OrderTicket, get_updatable_fields
from app.models.ticket_holder import TicketHolder
from app.models.user import User
from app.settings import get_settings

order_misc_routes = Blueprint('order_misc', __name__, url_prefix='/v1')
alipay_blueprint = Blueprint('alipay_blueprint', __name__, url_prefix='/v1/alipay')
stripe_blueprint = Blueprint('stripe_blueprint', __name__, url_prefix='/v1/stripe')


def check_event_user_ticket_holders(order, data, element):
    if element in ['event', 'user'] and data[element] != str(
        getattr(order, element, None).id
    ):
        raise ForbiddenError(
            {'pointer': f'data/{element}'},
            f"You cannot update {element} of an order",
        )
    if element == 'ticket_holders':
        ticket_holders = []
        for ticket_holder in order.ticket_holders:
            ticket_holders.append(str(ticket_holder.id))
        if data[element] != ticket_holders and element not in get_updatable_fields():
            raise ForbiddenError(
                {'pointer': f'data/{element}'},
                f"You cannot update {element} of an order",
            )


def is_payment_valid(order, mode):
    if mode == 'stripe':
        return (
            (order.paid_via == 'stripe')
            and order.brand
            and order.transaction_id
            and order.exp_year
            and order.last4
            and order.exp_month
        )
    if mode == 'paypal':
        return (order.paid_via == 'paypal') and order.transaction_id


def check_billing_info(data):
    if (
        data.get('amount')
        and data.get('amount') > 0
        and not data.get('is_billing_enabled')
    ):
        raise UnprocessableEntityError(
            {'pointer': '/data/attributes/is_billing_enabled'},
            "Billing information is mandatory for this order",
        )
    if data.get('is_billing_enabled') and not (
        data.get('company')
        and data.get('address')
        and data.get('city')
        and data.get('zipcode')
        and data.get('country')
    ):
        raise UnprocessableEntityError(
            {'pointer': '/data/attributes/is_billing_enabled'},
            "Billing information incomplete",
        )


def save_order(order):
    order_tickets = {}
    for holder in order.ticket_holders:
        save_to_db(holder)
        if not order_tickets.get(holder.ticket_id):
            order_tickets[holder.ticket_id] = 1
        else:
            order_tickets[holder.ticket_id] += 1

    order.user = current_user

    for ticket in order_tickets:
        od = OrderTicket(
            order_id=order.id, ticket_id=ticket, quantity=order_tickets[ticket]
        )
        save_to_db(od)

    order.quantity = order.tickets_count
    save_to_db(order)

    on_order_completed(order)


def validate_attendees(ticket_holders):
    free_ticket_quantity = 0

    for ticket_holder in validate_ticket_holders(ticket_holders):
        if ticket_holder.ticket.type == 'free':
            free_ticket_quantity += 1

    if not current_app.config['ALLOW_UNVERIFIED_FREE_ORDERS'] and (
        not current_user.is_verified and free_ticket_quantity == len(ticket_holders)
    ):
        raise ForbiddenError(
            {'pointer': '/data/relationships/user', 'code': 'unverified-user'},
            "Unverified user cannot place free orders",
        )


class OrdersListPost(ResourceList):
    """
    OrderListPost class for OrderSchema
    """

    def before_post(self, args, kwargs, data=None):
        """
        before post method to check for required relationships and permissions
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['event'], data)

        # Create on site attendees.
        if request.args.get('onsite', False):
            create_onsite_attendees_for_order(data)
        elif data.get('on_site_tickets'):
            del data['on_site_tickets']
        require_relationship(['ticket_holders'], data)

        # Ensuring that default status is always initializing, unless the user is event co-organizer
        if not has_access('is_coorganizer', event_id=data['event']):
            data['status'] = 'initializing'

    def before_create_object(self, data, view_kwargs):
        """
        before create object method for OrderListPost Class
        :param data:
        :param view_kwargs:
        :return:
        """
        validate_attendees(data['ticket_holders'])

        if data.get('cancel_note'):
            del data['cancel_note']

        if data.get('payment_mode') != 'free' and not data.get('amount'):
            raise ConflictError(
                {'pointer': '/data/attributes/amount'},
                "Amount cannot be null for a paid order",
            )

        if not data.get('amount'):
            data['amount'] = 0
        # Apply discount only if the user is not event admin
        if data.get('discount_code') and not has_access(
            'is_coorganizer', event_id=data['event']
        ):
            validate_discount_code(
                data['discount_code'],
                ticket_holders=data['ticket_holders'],
                event_id=data['event'],
            )

    def after_create_object(self, order, data, view_kwargs):
        """
        after create object method for OrderListPost Class
        :param order: Object created from mashmallow_jsonapi
        :param data:
        :param view_kwargs:
        :return:
        """
        save_order(order)

        data['user_id'] = current_user.id

    methods = [
        'POST',
    ]
    decorators = (jwt_required,)
    schema = OrderSchema
    data_layer = {
        'session': db.session,
        'model': Order,
        'methods': {
            'before_create_object': before_create_object,
            'after_create_object': after_create_object,
        },
    }


class OrdersList(ResourceList):
    """
    OrderList class for OrderSchema
    """

    def query(self, view_kwargs):
        query_ = self.session.query(Order)
        if view_kwargs.get('user_id'):
            # orders under a user
            user = safe_query_kwargs(User, view_kwargs, 'user_id')
            if not has_access('is_user_itself', user_id=user.id):
                raise ForbiddenError({'source': ''}, 'Access Forbidden')
            query_ = query_.join(TicketHolder).filter(TicketHolder.email == user.email)
        else:
            # orders under an event
            query_ = event_query(query_, view_kwargs, restrict=True)

        return query_

    decorators = (jwt_required,)
    methods = [
        'GET',
    ]
    schema = OrderSchema
    data_layer = {'session': db.session, 'model': Order, 'methods': {'query': query}}


class OrderDetail(ResourceDetail):
    """
    OrderDetail class for OrderSchema
    """

    def before_get_object(self, view_kwargs):
        """
        before get method to get the resource id for fetching details
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('attendee_id'):
            attendee = safe_query_kwargs(TicketHolder, view_kwargs, 'attendee_id')
            view_kwargs['id'] = attendee.order.id
        if view_kwargs.get('order_identifier'):
            order = safe_query_kwargs(
                Order, view_kwargs, 'order_identifier', 'identifier'
            )
            view_kwargs['id'] = order.id
        elif view_kwargs.get('id'):
            order = safe_query_by_id(Order, view_kwargs['id'])

        if not (
            has_access(
                'is_coorganizer_or_user_itself',
                event_id=order.event_id,
                user_id=order.user_id,
            )
            or order.is_attendee(current_user)
        ):
            raise ForbiddenError(
                {'source': ''}, 'You can only access your orders or your event\'s orders'
            )

    def before_update_object(self, order, data, view_kwargs):
        """
        before update object method of order details
        1. admin can update all the fields.
        2. event organizer
            a. own orders: he/she can update selected fields.
            b. other's orders: can only update the status that too when the order mode is free. No refund system.
        3. order user can update selected fields of his/her order when the status is initializing.
        The selected fields mentioned above can be taken from get_updatable_fields method from order model.
        :param order:
        :param data:
        :param view_kwargs:
        :return:
        """
        if (
            data.get('status') in ['pending', 'placed', 'completed']
            and order.event.is_ticket_form_enabled
        ):
            attendees = order.ticket_holders
            for attendee in attendees:
                validate_custom_form_constraints_request(
                    'attendee', AttendeeSchema, attendee, {}
                )

        if data.get('amount') and (
            data.get('is_billing_enabled') or order.event.is_billing_info_mandatory
        ):
            check_billing_info(data)
        if (not has_access('is_coorganizer', event_id=order.event_id)) and (
            not current_user.id == order.user_id
        ):
            raise ForbiddenError({'pointer': ''}, "Access Forbidden")

        relationships = ['event', 'ticket_holders', 'user']
        if has_access('is_coorganizer_but_not_admin', event_id=order.event_id):
            if current_user.id == order.user_id:
                # Order created from the tickets tab.
                for element in data:
                    if data[element]:
                        if (
                            element not in relationships
                            and data[element] != getattr(order, element, None)
                            and element not in get_updatable_fields()
                        ):
                            raise ForbiddenError(
                                {'pointer': f'data/{element}'},
                                f"You cannot update {element} of an order",
                            )
                        check_event_user_ticket_holders(order, data, element)

            else:
                # Order created from the public pages.
                for element in data:
                    if data[element]:
                        if element not in relationships and data[element] != getattr(
                            order, element, None
                        ):
                            if element != 'status':
                                raise ForbiddenError(
                                    {'pointer': f'data/{element}'},
                                    f"You cannot update {element} of an order",
                                )
                            if (
                                element == 'status'
                                and order.amount
                                and order.status == 'completed'
                            ):
                                # Since we don't have a refund system.
                                raise ForbiddenError(
                                    {'pointer': 'data/status'},
                                    "You cannot update the status of a completed paid order",
                                )
                            if element == 'status' and order.status == 'cancelled':
                                # Since the tickets have been unlocked and we can't revert it.
                                raise ForbiddenError(
                                    {'pointer': 'data/status'},
                                    "You cannot update the status of a cancelled order",
                                )
                        else:
                            check_event_user_ticket_holders(order, data, element)

        elif current_user.id == order.user_id:
            status = data.get('status')
            if (
                order.status != Order.Status.INITIALIZING
                and order.status != Order.Status.PENDING
                and status != Order.Status.CANCELLED
            ):
                raise ForbiddenError(
                    {'pointer': ''},
                    "You cannot update a non-initialized or non-pending order",
                )
            if status == Order.Status.CANCELLED:
                # If this is a cancellation request, we revert all PATCH changes except status = cancelled
                data.clear()
                data['status'] = Order.Status.CANCELLED
            for element in data:
                if data[element]:
                    if (
                        element == 'is_billing_enabled'
                        and order.status == 'completed'
                        and data[element] != getattr(order, element, None)
                    ):
                        raise ForbiddenError(
                            {'pointer': f'data/{element}'},
                            f"You cannot update {element} of a completed order",
                        )
                    if (
                        element not in relationships
                        and data[element] != getattr(order, element, None)
                        and element not in get_updatable_fields()
                    ):
                        raise ForbiddenError(
                            {'pointer': f'data/{element}'},
                            f"You cannot update {element} of an order",
                        )
                    check_event_user_ticket_holders(order, data, element)

        if has_access('is_organizer', event_id=order.event_id) and 'order_notes' in data:
            if order.order_notes and data['order_notes'] not in order.order_notes.split(
                ","
            ):
                data['order_notes'] = '{},{}'.format(
                    order.order_notes, data['order_notes']
                )

        if data.get('payment_mode') == 'free' and data.get('amount') > 0:
            raise UnprocessableEntityError(
                {'pointer': '/data/attributes/payment-mode'},
                "payment-mode cannot be free for order with amount > 0",
            )
        if (
            data.get('status') == 'completed'
            and data.get('payment_mode') == 'stripe'
            and not is_payment_valid(order, 'stripe')
        ):
            raise UnprocessableEntityError(
                {'pointer': '/data/attributes/payment-mode'},
                "insufficient data to verify stripe payment",
            )
        if (
            data.get('status') == 'completed'
            and data.get('payment_mode') == 'paypal'
            and not is_payment_valid(order, 'paypal')
        ):
            raise UnprocessableEntityError(
                {'pointer': '/data/attributes/payment-mode'},
                "insufficient data to verify paypal payment",
            )

    def after_update_object(self, order, data, view_kwargs):
        """
        :param order:
        :param data:
        :param view_kwargs:
        :return:
        """

        if order.status == 'cancelled':
            send_order_cancel_email(order)
            notify_ticket_cancel(order, current_user)

            # delete the attendees so that the tickets are unlocked.
            delete_related_attendees_for_order(order)

        elif order.status == 'completed' or order.status == 'placed':
            on_order_completed(order)

    # This is to ensure that the permissions manager runs and hence changes the kwarg from order identifier to id.
    decorators = (
        jwt_required,
        api.has_permission('auth_required', methods="PATCH", model=Order),
    )
    schema = OrderSchema
    data_layer = {
        'session': db.session,
        'model': Order,
        'methods': {
            'before_update_object': before_update_object,
            'before_get_object': before_get_object,
            'after_update_object': after_update_object,
        },
    }


class OrderRelationship(ResourceRelationship):
    """
    Order relationship
    """

    def before_get(self, args, kwargs):
        """
        before get method to get the resource id for fetching details
        :param view_kwargs:
        :return:
        """
        if kwargs.get('order_identifier'):
            order = safe_query_kwargs(Order, kwargs, 'order_identifier', 'identifier')
            kwargs['id'] = order.id
        elif kwargs.get('id'):
            order = safe_query_by_id(Order, kwargs['id'])

        if not has_access(
            'is_coorganizer', event_id=order.event_id, user_id=order.user_id
        ):
            raise ForbiddenError(
                {'source': ''}, 'You can only access your orders or your event\'s orders'
            )

    decorators = (jwt_required,)
    schema = OrderSchema
    data_layer = {'session': db.session, 'model': Order}


class ChargeSchema(Schema):
    """
    ChargeSchema
    """

    class Meta:
        """
        Meta class for ChargeSchema
        """

        type_ = 'charge'
        inflect = dasherize
        self_view = 'v1.charge_list'
        self_view_kwargs = {'order_identifier': '<id>'}

    id = fields.Str(dump_only=True)
    stripe = fields.Str(load_only=True, allow_none=True)
    paypal_payer_id = fields.Str(load_only=True, allow_none=True)
    paypal_payment_id = fields.Str(load_only=True, allow_none=True)
    status = fields.Boolean(dump_only=True)
    message = fields.Str(dump_only=True)


class ChargeList(ResourceList):
    """
    ChargeList ResourceList for ChargesLayer class
    """

    methods = [
        'POST',
    ]
    schema = ChargeSchema

    data_layer = {'class': ChargesLayer, 'session': db.session, 'model': Order}

    decorators = (jwt_required,)


@order_misc_routes.route(
    '/orders/<string:order_identifier>/create-paypal-payment', methods=['POST']
)
@jwt_required
def create_paypal_payment(order_identifier):
    """
    Create a paypal payment.
    :return: The payment id of the created payment.
    """
    try:
        return_url = request.json['data']['attributes']['return-url']
        cancel_url = request.json['data']['attributes']['cancel-url']
    except TypeError:
        raise BadRequestError({'source': ''}, 'Bad Request Error')

    order = safe_query(Order, 'identifier', order_identifier, 'identifier')
    status, response = PayPalPaymentsManager.create_payment(order, return_url, cancel_url)

    if status:
        return jsonify(status=True, payment_id=response)
    return jsonify(status=False, error=response)


@order_misc_routes.route(
    '/orders/<string:order_identifier>/verify-mobile-paypal-payment', methods=['POST']
)
@jwt_required
def verify_mobile_paypal_payment(order_identifier):
    """
    Verify paypal payment made on mobile client
    :return: The status of order verification
    """
    try:
        payment_id = request.json['data']['attributes']['payment-id']
    except TypeError:
        raise BadRequestError({'source': ''}, 'Bad Request Error')
    order = safe_query(Order, 'identifier', order_identifier, 'identifier')
    status, error = PayPalPaymentsManager.verify_payment(payment_id, order)
    return jsonify(status=status, error=error)


@alipay_blueprint.route(
    '/create_source/<string:order_identifier>', methods=['GET', 'POST']
)
@jwt_required
def create_source(order_identifier):
    """
    Create a source object for alipay payments.
    :param order_identifier:
    :return: The alipay redirection link.
    """
    try:
        order = safe_query(Order, 'identifier', order_identifier, 'identifier')
        source_object = AliPayPaymentsManager.create_source(
            amount=int(order.amount),
            currency='usd',
            redirect_return_uri=url_for(
                'alipay_blueprint.alipay_return_uri',
                order_identifier=order.identifier,
                _external=True,
            ),
        )
        order.order_notes = source_object.id
        save_to_db(order)
        return jsonify(link=source_object.redirect['url'])
    except TypeError:
        raise BadRequestError({'source': ''}, 'Source creation error')


@alipay_blueprint.route(
    '/alipay_return_uri/<string:order_identifier>', methods=['GET', 'POST']
)
def alipay_return_uri(order_identifier):
    """
    Charge Object creation & Order finalization for Alipay payments.
    :param order_identifier:
    :return: JSON response of the payment status.
    """
    try:
        charge_response = AliPayPaymentsManager.charge_source(order_identifier)
        if charge_response.status == 'succeeded':
            order = safe_query(Order, 'identifier', order_identifier, 'identifier')
            order.status = 'completed'
            save_to_db(order)
            return redirect(make_frontend_url(f'/orders/{order_identifier}/view'))
        return jsonify(status=False, error='Charge object failure')
    except TypeError:
        return jsonify(status=False, error='Source object status error')


@order_misc_routes.route(
    '/orders/<string:order_identifier>/omise-checkout', methods=['POST', 'GET']
)
@jwt_required
def omise_checkout(order_identifier):
    """
    Charging the user and returning payment response for Omise Gateway
    :param order_identifier:
    :return: JSON response of the payment status.
    """
    token = request.form.get('omiseToken')
    order = safe_query(Order, 'identifier', order_identifier, 'identifier')
    order.status = 'completed'
    save_to_db(order)
    try:
        charge = OmisePaymentsManager.charge_payment(order_identifier, token)
    except omise.errors.BaseError as e:
        logging.exception(
            f"""OmiseError: {repr(e)}.  See https://www.omise.co/api-errors"""
        )
        return jsonify(status=False, error=f"Omise Failure Message: {str(e)}")
    except Exception:
        logging.exception('Error while charging omise')
    if charge.failure_code is not None:
        logging.warning(
            "Omise Failure Message: {} ({})".format(
                charge.failure_message, charge.failure_code
            )
        )
        return jsonify(
            status=False,
            error="Omise Failure Message: {} ({})".format(
                charge.failure_message, charge.failure_code
            ),
        )
    logging.info(f"Successful charge: {charge.id}.  Order ID: {order_identifier}")

    return redirect(make_frontend_url(f'orders/{order_identifier}/view'))


@order_misc_routes.route(
    '/orders/<string:order_identifier>/paytm/initiate-transaction',
    methods=['POST', 'GET'],
)
@jwt_required
def initiate_transaction(order_identifier):
    """
    Initiating a PayTM transaction to obtain the txn token
    :param order_identifier:
    :return: JSON response containing the signature & txn token
    """
    order = safe_query(Order, 'identifier', order_identifier, 'identifier')
    paytm_mode = get_settings()['paytm_mode']
    paytm_params = {}
    # body parameters
    paytm_params["body"] = {
        "requestType": "Payment",
        "mid": (
            get_settings()['paytm_sandbox_merchant']
            if paytm_mode == 'test'
            else get_settings()['paytm_live_merchant']
        ),
        "websiteName": "eventyay",
        "orderId": order_identifier,
        "callbackUrl": "",
        "txnAmount": {
            "value": order.amount,
            "currency": "INR",
        },
        "userInfo": {
            "custId": order.user.id,
        },
    }
    checksum = PaytmPaymentsManager.generate_checksum(paytm_params)
    # head parameters
    paytm_params["head"] = {"signature": checksum}
    post_data = json.dumps(paytm_params)
    if paytm_mode == 'test':
        url = "https://securegw-stage.paytm.in/theia/api/v1/initiateTransaction?mid={}&orderId={}".format(
            get_settings()['paytm_sandbox_merchant'], order_identifier
        )
    else:
        url = "https://securegw.paytm.in/theia/api/v1/initiateTransaction?mid={}&orderId={}".format(
            get_settings()['paytm_live_merchant'], order_identifier
        )
    response = requests.post(
        url, data=post_data, headers={"Content-type": "application/json"}
    )
    return response.json()


@order_misc_routes.route(
    '/orders/<string:order_identifier>/paytm/fetch-payment-options/<string:txn_token>'
)
@jwt_required
def fetch_payment_options(order_identifier, txn_token):
    paytm_mode = get_settings()['paytm_mode']
    if paytm_mode == 'test':
        url = "https://securegw-stage.paytm.in/theia/api/v1/fetchPaymentOptions?mid={}&orderId={}".format(
            get_settings()['paytm_sandbox_merchant'], order_identifier
        )
    else:
        url = "https://securegw.paytm.in/theia/api/v1/fetchPaymentOptions?mid={}&orderId={}".format(
            get_settings()['paytm_live_merchant'], order_identifier
        )
    head = {
        "clientId": "C11",
        "version": "v1",
        "requestTimestamp": str(int(time.time())),
        "channelId": "WEB",
        "txnToken": txn_token,
    }
    response = PaytmPaymentsManager.hit_paytm_endpoint(url=url, head=head)
    return response


@order_misc_routes.route(
    '/orders/<string:order_identifier>/paytm/send_otp/<string:txn_token>',
    methods=['POST'],
)
@jwt_required
def send_otp(order_identifier, txn_token):
    paytm_mode = get_settings()['paytm_mode']
    if paytm_mode == 'test':
        url = "https://securegw-stage.paytm.in/theia/api/v1/login/sendOtp?mid={}&orderId={}".format(
            get_settings()['paytm_sandbox_merchant'], order_identifier
        )
    else:
        url = "https://securegw.paytm.in/theia/api/v1/login/sendOtp?mid={}&orderId={}".format(
            get_settings()['paytm_live_merchant'], order_identifier
        )

    head = {
        "clientId": "C11",
        "version": "v1",
        "requestTimestamp": str(int(time.time())),
        "channelId": "WEB",
        "txnToken": txn_token,
    }
    body = {"mobileNumber": request.json['data']['phone']}
    response = PaytmPaymentsManager.hit_paytm_endpoint(url=url, head=head, body=body)
    return response


@order_misc_routes.route(
    '/orders/<string:order_identifier>/paytm/validate_otp/<string:txn_token>',
    methods=['POST'],
)
def validate_otp(order_identifier, txn_token):
    paytm_mode = get_settings()['paytm_mode']
    if paytm_mode == 'test':
        url = "https://securegw-stage.paytm.in/theia/api/v1/login/validateOtp?mid={}&orderId={}".format(
            get_settings()['paytm_sandbox_merchant'], order_identifier
        )
    else:
        url = "https://securegw.paytm.in/theia/api/v1/login/validateOtp?mid={}&orderId={}".format(
            get_settings()['paytm_live_merchant'], order_identifier
        )
    head = {
        "clientId": "C11",
        "version": "v1",
        "requestTimestamp": str(int(time.time())),
        "channelId": "WEB",
        "txnToken": txn_token,
    }
    body = {"otp": request.json['data']['otp']}
    response = PaytmPaymentsManager.hit_paytm_endpoint(url=url, head=head, body=body)
    return response


@order_misc_routes.route(
    '/orders/<string:order_identifier>/paytm/process_transaction/<string:txn_token>'
)
@jwt_required
def process_transaction(order_identifier, txn_token):
    paytm_mode = get_settings()['paytm_mode']
    merchant_id = (
        get_settings()['paytm_sandbox_merchant']
        if paytm_mode == 'test'
        else get_settings()['paytm_live_merchant']
    )

    if paytm_mode == 'test':
        url = "https://securegw-stage.paytm.in/theia/api/v1/processTransaction?mid={}&orderId={}".format(
            get_settings()['paytm_sandbox_merchant'], order_identifier
        )
    else:
        url = "https://securegw.paytm.in/theia/api/v1/processTransaction?mid={}&orderId={}".format(
            get_settings()['paytm_live_merchant'], order_identifier
        )

    head = {
        "version": "v1",
        "requestTimestamp": str(int(time.time())),
        "channelId": "WEB",
        "txnToken": txn_token,
    }

    body = {
        "requestType": "NATIVE",
        "mid": merchant_id,
        "orderId": order_identifier,
        "paymentMode": "BALANCE",
    }

    response = PaytmPaymentsManager.hit_paytm_endpoint(url=url, head=head, body=body)
    return response


@order_misc_routes.route(
    '/orders/<string:order_identifier>/paytm/transaction-status', methods=['GET']
)
def get_transaction_status(order_identifier):
    paytm_params = {}
    paytm_checksum_params = {}
    url = ""
    paytm_mode = get_settings()['paytm_mode']
    merchant_id = (
        get_settings()['paytm_sandbox_merchant']
        if paytm_mode == 'test'
        else get_settings()['paytm_live_merchant']
    )
    paytm_checksum_params["body"] = {"mid": merchant_id, "orderId": order_identifier}
    checksum = PaytmPaymentsManager.generate_checksum(paytm_checksum_params)

    paytm_params["MID"] = merchant_id
    paytm_params["ORDERID"] = order_identifier
    paytm_params["CHECKSUMHASH"] = checksum
    post_data = json.dumps(paytm_params)

    if paytm_mode == 'test':
        url = "https://securegw-stage.paytm.in/order/status"
    else:
        url = "https://securegw.paytm.in/order/status"
    response = requests.post(
        url, data=post_data, headers={"Content-type": "application/json"}
    ).json()
    return response
