from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from sqlalchemy.orm.exc import NoResultFound
from flask_rest_jsonapi.exceptions import ObjectNotFound
from flask import request

from app.api.helpers.utilities import dasherize
from app.models import db
from app.api.helpers.permissions import jwt_required
from app.models.event import Event
from app.models.tax import Tax
from app.api.helpers.db import safe_query
from app.api.helpers.utilities import require_relationship
from app.api.bootstrap import api
from app.api.helpers.permission_manager import has_access
from app.api.helpers.exceptions import ForbiddenException


class TaxSchemaPublic(Schema):
    class Meta:
        type_ = 'tax'
        self_view = 'v1.tax_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    rate = fields.Float(validate=lambda n: 0 <= n <= 100, required=True)
    is_tax_included_in_price = fields.Boolean(default=False)
    event = Relationship(attribute='event',
                         self_view='v1.tax_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'tax_id': '<id>'},
                         schema='EventSchema',
                         type_='event')


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


class TaxListPost(ResourceList):
    def before_post(self, args, kwargs, data):
        require_relationship(['event'], data)
        if not has_access('is_coorganizer', event_id=data['event']):
            raise ForbiddenException({'source': ''}, 'Co-organizer access is required.')

    def before_get(self, args, kwargs):
        if 'Authorization' in request.headers and has_access('is_admin'):
            self.schema = TaxSchema
        else:
            self.schema = TaxSchemaPublic

    schema = TaxSchema
    data_layer = {'session': db.session,
                  'model': Tax}


class TaxList(ResourceList):
    def before_get(self, args, view_kwargs):
        if view_kwargs.get('event_identifier'):
            try:
                event = Tax.query.filter_by(identifier=view_kwargs['id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'event_identifier'},
                                     "Event: {} not found".format(view_kwargs['event_identifier']))
            else:
                view_kwargs['event_id'] = event.id

        if has_access('is_coorganizer', event_id=view_kwargs['event_id']):
            self.schema = TaxSchema
        else:
            self.schema = TaxSchemaPublic

    def query(self, view_kwargs):
        query_ = self.session.query(Tax)
        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
            query_ = query_.join(Event).filter(Event.id == event.id)
        elif view_kwargs.get('identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
            query_ = query_.join(Event).filter(Event.identifier == event.id)
        return query_

    view_kwargs = True
    methods = ['GET', ]
    schema = TaxSchema
    data_layer = {'session': db.session,
                  'model': Tax,
                  'methods': {
                      'query': query
                  }}


class TaxDetail(ResourceDetail):
    """
     tax detail by id
    """

    def before_get(self, args, kwargs):
        tax = Tax.query.filter_by(id=kwargs['id']).one()
        if 'Authorization' in request.headers and has_access('is_coorganizer', event_id=tax.event_id):
            self.schema = TaxSchema
        else:
            self.schema = TaxSchemaPublic

    decorators = (api.has_permission('is_coorganizer', fetch="event_id",
                                     fetch_as="event_id", model=Tax, methods="PATCH,DELETE"),)
    schema = TaxSchema
    data_layer = {'session': db.session,
                  'model': Tax}


class TaxRelationship(ResourceRelationship):
    decorators = (jwt_required,)
    methods = ['GET', 'PATCH']
    schema = TaxSchema
    data_layer = {'session': db.session,
                  'model': Tax}
