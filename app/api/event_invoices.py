from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields

from app.api.helpers.utilities import dasherize
from app.api.helpers.permissions import is_admin
from app.models import db
from app.models.event import Event
from app.models.user import User
from app.models.event_invoice import EventInvoice


class EventInvoiceSchema(Schema):

    class Meta:
        type_ = 'event_invoice'
        self_view = 'v1.event_invoice_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    identifier = fields.Str()
    amount = fields.Float()
    address = fields.Str()
    city = fields.Str()
    state = fields.Str()
    country = fields.Str()
    zipcode = fields.Str()
    created_at = fields.DateTime()
    completed_at = fields.DateTime(default=None)
    transaction_id = fields.Str()
    paid_via = fields.Str()
    payment_mode = fields.Str()
    brand = fields.Str()
    exp_month = fields.Integer()
    exp_year = fields.Integer()
    last4 = fields.Str()
    stripe_token = fields.Str()
    paypal_token = fields.Str()
    status = fields.Str()
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


class EventInvoiceList(ResourceList):
    """
    List and Create Event Invoices
    """

    def query(self, view_kwargs):
        query_ = self.session.query(EventInvoice)
        if view_kwargs.get('event_id') is not None:
            query_ = query_.filter_by(event_id=view_kwargs['event_id'])
        if view_kwargs.get('user_id') is not None:
            query_ = query_.filter_by(user_id=view_kwargs['user_id'])
        return query_

    def before_create_object(self, data, view_kwargs):
        if view_kwargs.get('event_id') is not None:
            event = self.session.query(Event).filter_by(id=view_kwargs['event_id']).one()
            data['event_id'] = event.id
        if view_kwargs.get('user_id') is not None:
            user = self.session.query(User).filter_by(id=view_kwargs['user_id']).one()
            data['user_id'] = user.id

    view_kwargs = True
    decorators = (is_admin, )
    schema = EventInvoiceSchema
    data_layer = {'session': db.session,
                  'model': EventInvoice,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object}}


class EventInvoiceDetail(ResourceDetail):
    """
    Event Invoice detail by id
    """
    decorators = (is_admin, )
    schema = EventInvoiceSchema
    data_layer = {'session': db.session,
                  'model': EventInvoice}


class EventInvoiceRelationship(ResourceRelationship):
    """
    Event Invoice Relationship
    """
    decorators = (is_admin, )
    schema = EventInvoiceSchema
    data_layer = {'session': db.session,
                  'model': EventInvoice}
