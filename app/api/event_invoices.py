from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
import marshmallow.validate as validate

from app.api.helpers.utilities import dasherize
from app.api.helpers.permissions import is_admin
from app.models import db
from app.models.user import User
from app.models.event_invoice import EventInvoice
from app.models.discount_code import DiscountCode
from app.api.helpers.static import PAYMENT_COUNTRIES
from app.api.helpers.db import safe_query
from app.api.helpers.utilities import require_relationship
from app.api.helpers.exceptions import ForbiddenException
from app.api.helpers.permission_manager import has_access
from app.api.bootstrap import api
from app.api.helpers.query import event_query


class EventInvoiceSchema(Schema):
    """
    Event Invoice API Schema based on event invoice model
    """
    class Meta:
        type_ = 'event-invoice'
        self_view = 'v1.event_invoice_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    identifier = fields.Str(allow_none=True)
    amount = fields.Float(validate=lambda n: n >= 0, allow_none=True)
    address = fields.Str(allow_none=True)
    city = fields.Str(allow_none=True)
    state = fields.Str(allow_none=True)
    country = fields.Str(validate=validate.OneOf(choices=PAYMENT_COUNTRIES), allow_none=True)
    zipcode = fields.Str(allow_none=True)
    created_at = fields.DateTime(allow_none=True)
    completed_at = fields.DateTime(default=None)
    transaction_id = fields.Str(allow_none=True)
    paid_via = fields.Str(validate=validate.OneOf(
        choices=["free", "stripe", "paypal", "transfer", "onsite", "cheque"]), allow_none=True)
    payment_mode = fields.Str(allow_none=True)
    brand = fields.Str(allow_none=True)
    exp_month = fields.Integer(validate=lambda n: 0 <= n <= 12, allow_none=True)
    exp_year = fields.Integer(validate=lambda n: n >= 2015, allow_none=True)
    last4 = fields.Str(allow_none=True)
    stripe_token = fields.Str(allow_none=True)
    paypal_token = fields.Str(allow_none=True)
    status = fields.Str(validate=validate.OneOf(
        choices=["expired", "deleted", "initialized" "completed", "placed", "pending", "cancelled"]), allow_none=True)
    invoice_pdf_url = fields.Url(allow_none=True)
    user = Relationship(attribute='user',
                        self_view='v1.event_invoice_user',
                        self_view_kwargs={'id': '<id>'},
                        related_view='v1.user_detail',
                        related_view_kwargs={'event_invoice_id': '<id>'},
                        schema='UserSchema',
                        type_='user')
    event = Relationship(attribute='event',
                         self_view='v1.event_invoice_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'event_invoice_id': '<id>'},
                         schema='EventSchema',
                         type_='event')
    discount_codes = Relationship(attribute='discount_code',
                                  many=True,
                                  self_view='v1.event_invoice_discount_code',
                                  self_view_kwargs={'id': '<id>'},
                                  related_view='v1.discount_code_detail',
                                  related_view_kwargs={'event_invoice_id': '<id>'},
                                  schema='DiscountCodeSchema',
                                  type_='discount-code')


class EventInvoiceList(ResourceList):
    """
    List and Create Event Invoices
    """
    def before_post(self, args, kwargs, data):
        require_relationship(['event'], data)

    def query(self, view_kwargs):
        """
        query method for event invoice list
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(EventInvoice)
        query_ = event_query(self, query_, view_kwargs)
        if view_kwargs.get('user_id'):
            user = safe_query(self, User, 'id', view_kwargs['user_id'], 'user_id')
            query_ = query_.join(User).filter(User.id == user.id)
        if view_kwargs.get('discount_code_id'):
            discount_code = safe_query(self, DiscountCode, 'id', view_kwargs['discount_code_id'], 'discount_code_id')
            query_ = query_.join(DiscountCode).filter(DiscountCode.id == discount_code.id)
        return query_

    view_kwargs = True
    methods = ['GET', ]
    decorators = (api.has_permission('is_organizer', ), )
    schema = EventInvoiceSchema
    data_layer = {'session': db.session,
                  'model': EventInvoice,
                  'methods': {
                      'query': query
                  }}


class EventInvoiceDetail(ResourceDetail):
    """
    Event Invoice detail by id
    """
    decorators = (is_admin,)
    schema = EventInvoiceSchema
    data_layer = {'session': db.session,
                  'model': EventInvoice}


class EventInvoiceRelationshipRequired(ResourceRelationship):
    """
    Event Invoice Relationship for required entities
    """
    decorators = (is_admin,)
    methods = ['GET', 'PATCH']
    schema = EventInvoiceSchema
    data_layer = {'session': db.session,
                  'model': EventInvoice}


class EventInvoiceRelationshipOptional(ResourceRelationship):
    """
    Event Invoice Relationship
    """
    decorators = (is_admin,)
    schema = EventInvoiceSchema
    data_layer = {'session': db.session,
                  'model': EventInvoice}
