from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from marshmallow import validates_schema
import marshmallow.validate as validate
from sqlalchemy.orm.exc import NoResultFound
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.helpers.utilities import dasherize
from app.api.helpers.permissions import jwt_required
from app.models import db
from app.models.event import Event
from app.models.discount_code import DiscountCode
from app.api.helpers.exceptions import UnprocessableEntity


class DiscountCodeSchema(Schema):
    """
    API Schema for discount_code Model
    """

    class Meta:
        type_ = 'discount-code'
        self_view = 'v1.discount_code_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    @validates_schema(pass_original=True)
    def validate_quantity(self, data, original_data):
        if 'id' in original_data['data']:
            discount_code = DiscountCode.query.filter_by(id=original_data['data']['id']).one()
            if 'min_quantity' not in data:
                data['min_quantity'] = discount_code.min_quantity

            if 'max_quantity' not in data:
                data['max_quantity'] = discount_code.max_quantity

            if 'tickets_number' not in data:
                data['tickets_number'] = discount_code.tickets_number

        if 'min_quantity' not in data or 'max_quantity' not in data:
            if data['min_quantity'] >= data['max_quantity']:
                raise UnprocessableEntity({'pointer': '/data/attributes/min-quantity'},
                                          "min-quantity should be less than max-quantity")

        if 'tickets_number' not in data or 'max_quantity' not in data:
            if data['tickets_number'] < data['min_quantity']:
                    raise UnprocessableEntity({'pointer': '/data/attributes/tickets-number'},
                                              "tickets-number should be greater than min-quantity")

    id = fields.Integer()
    code = fields.Str()
    discount_url = fields.Url()
    value = fields.Float()
    type = fields.Str(validate=validate.OneOf(choices=["amount", "percent"]))
    is_active = fields.Boolean()
    tickets_number = fields.Integer(validate=lambda n: n >= 0)
    min_quantity = fields.Integer(validate=lambda n: n >= 0)
    max_quantity = fields.Integer(validate=lambda n: n >= 0)
    valid_from = fields.DateTime()
    valid_till = fields.DateTime()
    tickets = fields.Str(validate=validate.OneOf(choices=["event", "ticket"]))
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
        """
        query method for Discount Code List
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(DiscountCode)
        if view_kwargs.get('event_id'):
            try:
                event = self.session.query(Event).filter_by(id=view_kwargs['event_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'event_id'},
                                     "Event: {} not found".format(view_kwargs['event_id']))
            else:
                query_ = query_.filter_by(event_id=event.id)
        elif view_kwargs.get('event_identifier'):
            try:
                event = self.session.query(Event).filter_by(identifier=view_kwargs['event_identifier']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'event_identifier'},
                                     "Event: {} not found".format(view_kwargs['event_identifier']))
            else:
                query_ = query_.join(Event).filter(Event.id == event.id)
        return query_

    def before_create_object(self, data, view_kwargs):
        """
        Method to create object before posting
        :param data:
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('event_id'):
            try:
                event = self.session.query(Event).filter_by(id=view_kwargs['event_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'event_id'},
                                     "Event: {} not found".format(view_kwargs['event_id']))
            else:
                data['event_id'] = event.id

        elif view_kwargs.get('event_identifier'):
            try:
                event = self.session.query(Event).filter_by(identifier=view_kwargs['event_identifier']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'event_identifier'},
                                     "Event: {} not found".format(view_kwargs['event_identifier']))
            else:
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
