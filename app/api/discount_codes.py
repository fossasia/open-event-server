from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields

from app.api.helpers.utilities import dasherize
from app.api.helpers.permissions import jwt_required
from app.models import db
from app.models.event import Event
from app.models.discount_code import DiscountCode


class DiscountCodeSchema(Schema):
    """
    API Schema for discount_code Model
    """

    class Meta:
        type_ = 'discount-code'
        self_view = 'v1.discount_code_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Integer()
    code = fields.Str()
    discount_url = fields.Url()
    value = fields.Float()
    type = fields.Str()
    is_active = fields.Boolean()
    tickets_number = fields.Integer()
    min_quantity = fields.Integer()
    max_quantity = fields.Integer()
    valid_from = fields.DateTime()
    valid_till = fields.DateTime()
    tickets = fields.Str()
    created_at = fields.DateTime()
    used_for = fields.Str()
    event = Relationship(attribute='event',
                         self_view='v1.discount_code_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'discount_code_id': '<id>'},
                         schema='EventSchema',
                         type_='event')


class DiscountCodeList(ResourceList):
    """
    List and Create Discount Code
    """

    def query(self, view_kwargs):
        query_ = self.session.query(DiscountCode)
        if view_kwargs.get('event_id') is not None:
            query_ = query_.filter_by(event_id=view_kwargs['event_id'])
        return query_

    def before_create_object(self, data, view_kwargs):
        if view_kwargs.get('event_id') is not None:
            event = self.session.query(Event).filter_by(id=view_kwargs['event_id']).one()
            data['event_id'] = event.id

    view_kwargs = True
    decorators = (jwt_required,)
    schema = DiscountCodeSchema
    data_layer = {'session': db.session,
                  'model': DiscountCode,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object}}


class DiscountCodeDetail(ResourceDetail):
    """
    Discount Code detail by id
    """
    decorators = (jwt_required,)
    schema = DiscountCodeSchema
    data_layer = {'session': db.session,
                  'model': DiscountCode}


class DiscountCodeRelationship(ResourceRelationship):
    """
    Discount Code Relationship
    """
    decorators = (jwt_required,)
    schema = DiscountCodeSchema
    data_layer = {'session': db.session,
                  'model': DiscountCode}
