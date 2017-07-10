from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from sqlalchemy.orm.exc import NoResultFound
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.helpers.utilities import dasherize
from app.models import db
from app.api.helpers.permissions import jwt_required
from app.models.event import Event
from app.models.tax import Tax
from app.api.helpers.db import safe_query


class TaxSchema(Schema):

    class Meta:
        type_ = 'tax'
        self_view = 'v1.tax_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    country = fields.Str(allow_none=True)
    name = fields.Str(required=True)
    rate = fields.Float(validate=lambda n: 0 <= n <= 100, required=True)
    tax_id = fields.Str(required=True)
    should_send_invoice = fields.Boolean(default=False)
    registered_company = fields.Str(allow_none=True)
    address = fields.Str(allow_none=True)
    city = fields.Str(allow_none=True)
    state = fields.Str(allow_none=True)
    zip = fields.Integer(allow_none=True)
    invoice_footer = fields.Str(allow_none=True)
    is_tax_included_in_price = fields.Boolean(default=False)
    event = Relationship(attribute='event',
                         self_view='v1.tax_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'tax_id': '<id>'},
                         schema='EventSchema',
                         type_='event')


class TaxList(ResourceList):

    def query(self, view_kwargs):
        query_ = self.session.query(Tax)
        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
            query_ = query_.join(Event).filter(Event.id == event.id)
        elif view_kwargs.get('identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
            query_ = query_.join(Event).filter(Event.identifier == event.id)
        return query_

    def before_create_object(self, data, view_kwargs):
        event = None
        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
        elif view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
        if event:
            data['event_id'] = event.id

    view_kwargs = True
    decorators = (jwt_required, )
    methods = ['POST', ]
    schema = TaxSchema
    data_layer = {'session': db.session,
                  'model': Tax,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object
                  }}


class TaxDetail(ResourceDetail):
    """
     tax detail by id
    """
    def before_get_object(self, view_kwargs):
        if view_kwargs.get('event_identifier'):
            try:
                event = self.session.query(Event).filter_by(identifier=view_kwargs['event_identifier']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'event_identifier'},
                                     "Event: {} not found".format(view_kwargs['event_identifier']))
            else:
                view_kwargs['event_id'] = event.id

        if view_kwargs.get('event_id'):
            try:
                event = self.session.query(Event).filter_by(id=view_kwargs['event_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'event_id'},
                                     "Event: {} not found".format(view_kwargs['event_id']))
            else:
                if event.tax:
                    view_kwargs['id'] = event.tax.id
                else:
                    view_kwargs['id'] = None

    decorators = (jwt_required, )
    schema = TaxSchema
    data_layer = {'session': db.session,
                  'model': Tax,
                  'methods': {
                      'before_get_object': before_get_object
                  }}


class TaxRelationship(ResourceRelationship):
    decorators = (jwt_required, )
    schema = TaxSchema
    data_layer = {'session': db.session,
                  'model': Tax}
