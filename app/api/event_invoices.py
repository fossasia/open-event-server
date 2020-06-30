import datetime

from flask import jsonify, request
from flask_jwt_extended import current_user
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.helpers.db import safe_query, safe_query_kwargs, save_to_db
from app.api.helpers.errors import BadRequestError, ForbiddenError
from app.api.helpers.payment import PayPalPaymentsManager
from app.api.helpers.permissions import is_admin, jwt_required
from app.api.helpers.query import event_query
from app.api.helpers.utilities import require_relationship
from app.api.orders import order_misc_routes
from app.api.schema.event_invoices import EventInvoiceSchema
from app.models import db
from app.models.discount_code import DiscountCode
from app.models.event_invoice import EventInvoice
from app.models.user import User


class EventInvoiceList(ResourceList):
    """
    List and Create Event Invoices
    """

    def before_post(self, args, kwargs, data):
        """
        before post method to check for required relationship and proper permission
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['event'], data)

    def query(self, view_kwargs):
        """
        query method for event invoice list
        :param view_kwargs:
        :return:
        """
        user = current_user
        if not user.is_staff:
            raise ForbiddenError({'source': ''}, 'Admin access is required')

        query_ = self.session.query(EventInvoice)
        query_ = event_query(query_, view_kwargs)
        if view_kwargs.get('user_id'):
            user = safe_query_kwargs(User, view_kwargs, 'user_id')
            query_ = query_.join(User).filter(User.id == user.id)
        if view_kwargs.get('discount_code_id'):
            discount_code = safe_query_kwargs(
                DiscountCode, view_kwargs, 'discount_code_id',
            )
            query_ = query_.join(DiscountCode).filter(DiscountCode.id == discount_code.id)
        return query_

    view_kwargs = True
    methods = [
        'GET',
    ]
    decorators = (api.has_permission('is_organizer',),)
    schema = EventInvoiceSchema
    data_layer = {
        'session': db.session,
        'model': EventInvoice,
        'methods': {'query': query},
    }


class EventInvoiceDetail(ResourceDetail):
    """
    Event Invoice detail by id
    """

    def before_get_object(self, view_kwargs):
        """
        before get method to get the resource id for fetching details
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('event_invoice_identifier'):
            event_invoice = safe_query_kwargs(
                EventInvoice, view_kwargs, 'event_invoice_identifier', 'identifier'
            )
            view_kwargs['id'] = event_invoice.id

    decorators = (is_admin,)
    schema = EventInvoiceSchema
    data_layer = {
        'session': db.session,
        'model': EventInvoice,
        'methods': {'before_get_object': before_get_object},
    }


class EventInvoiceRelationshipRequired(ResourceRelationship):
    """
    Event Invoice Relationship for required entities
    """

    def before_get_object(self, view_kwargs):
        """
        before get method to get the resource id for fetching details
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('event_invoice_identifier'):
            event_invoice = safe_query_kwargs(
                EventInvoice, view_kwargs, 'event_invoice_identifier', 'identifier'
            )
            view_kwargs['id'] = event_invoice.id

    decorators = (is_admin,)
    methods = ['GET', 'PATCH']
    schema = EventInvoiceSchema
    data_layer = {
        'session': db.session,
        'model': EventInvoice,
        'methods': {'before_get_object': before_get_object},
    }


class EventInvoiceRelationshipOptional(ResourceRelationship):
    """
    Event Invoice Relationship
    """

    def before_get_object(self, view_kwargs):
        """
        before get method to get the resource id for fetching details
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('event_invoice_identifier'):
            event_invoice = safe_query_kwargs(
                EventInvoice, view_kwargs, 'event_invoice_identifier', 'identifier'
            )
            view_kwargs['id'] = event_invoice.id

    decorators = (is_admin,)
    schema = EventInvoiceSchema
    data_layer = {
        'session': db.session,
        'model': EventInvoice,
        'methods': {'before_get_object': before_get_object},
    }


@order_misc_routes.route(
    '/event-invoices/<string:invoice_identifier>/create-paypal-payment',
    methods=['POST', 'GET'],
)
@jwt_required
def create_paypal_payment_invoice(invoice_identifier):
    """
    Create a paypal payment.
    :return: The payment id of the created payment.
    """
    try:
        return_url = request.json['data']['attributes']['return-url']
        cancel_url = request.json['data']['attributes']['cancel-url']
    except TypeError:
        raise BadRequestError({'source': ''}, 'Bad Request Error')

    event_invoice = safe_query(
        EventInvoice, 'identifier', invoice_identifier, 'identifier'
    )
    status, response = PayPalPaymentsManager.create_payment(
        event_invoice, return_url, cancel_url
    )

    if status:
        return jsonify(status=True, payment_id=response)
    else:
        return jsonify(status=False, error=response)


@order_misc_routes.route(
    '/event-invoices/<string:invoice_identifier>/charge', methods=['POST', 'GET']
)
@jwt_required
def charge_paypal_payment_invoice(invoice_identifier):
    """
    Create a paypal payment.
    :return: The payment id of the created payment.
    """
    try:
        paypal_payment_id = request.json['data']['attributes']['paypal_payment_id']
        paypal_payer_id = request.json['data']['attributes']['paypal_payer_id']
    except Exception as e:
        raise BadRequestError({'source': e}, 'Bad Request Error')
    event_invoice = safe_query(
        EventInvoice, 'identifier', invoice_identifier, 'identifier'
    )
    # save the paypal payment_id with the order
    event_invoice.paypal_token = paypal_payment_id
    save_to_db(event_invoice)

    # execute the invoice transaction.
    status, error = PayPalPaymentsManager.execute_payment(
        paypal_payer_id, paypal_payment_id
    )

    if status:
        # successful transaction hence update the order details.
        event_invoice.paid_via = 'paypal'
        event_invoice.status = 'paid'
        event_invoice.transaction_id = paypal_payment_id
        event_invoice.completed_at = datetime.datetime.now()
        save_to_db(event_invoice)

        return jsonify(status="Charge Successful", payment_id=paypal_payment_id)
    else:
        # return the error message from Paypal
        return jsonify(status="Charge Unsuccessful", error=error)
