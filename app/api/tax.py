from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields

from app.api.helpers.utilities import dasherize
from app.models import db
from app.api.helpers.permissions import jwt_required
from app.models.event import Event
from app.models.tax import Tax


class TaxSchema(Schema):

    class Meta:
        type_ = 'tax'
        self_view = 'v1.tax_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    country = fields.Str()
    name = fields.Str(required=True)
    rate = fields.Float(validate=lambda n: n >= 0, required=True)
    tax_id = fields.Str(required=True)
    should_send_invoice = fields.Boolean(default=False)
    registered_company = fields.Str()
    address = fields.Str()
    city = fields.Str()
    state = fields.Str()
    zip = fields.Integer()
    invoice_footer = fields.Str()
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
        if view_kwargs.get('id'):
            query_ = query_.join(Event).filter(Event.id == view_kwargs['id'])
        elif view_kwargs.get('identifier'):
            query_ = query_.join(Event).filter(Event.identifier == view_kwargs['identifier'])
        return query_

    def before_create_object(self, data, view_kwargs):
        if view_kwargs.get('id'):
            event = self.session.query(Event).filter_by(id=view_kwargs['id']).one()
            data['event_id'] = event.id

    view_kwargs = True
    decorators = (jwt_required, )
    schema = TaxSchema
    data_layer = {'session': db.session,
                  'model': Tax,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object
                  }}


class TaxDetail(ResourceDetail):
    decorators = (jwt_required, )
    schema = TaxSchema
    data_layer = {'session': db.session,
                  'model': Tax}


class TaxRelationship(ResourceRelationship):
    decorators = (jwt_required, )
    schema = TaxSchema
    data_layer = {'session': db.session,
                  'model': Tax}
