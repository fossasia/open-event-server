from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from marshmallow import validates_schema
import marshmallow.validate as validate
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.helpers.utilities import dasherize, require_relationship
from app.api.helpers.permissions import jwt_required, current_identity
from sqlalchemy.orm.exc import NoResultFound
from app.models import db
from app.models.event import Event
from app.models.user import User
from app.models.discount_code import DiscountCode
from app.api.helpers.exceptions import UnprocessableEntity, ForbiddenException
from app.api.helpers.db import safe_query
from app.api.helpers.permission_manager import has_access


class DiscountCodeSchemaTicket(Schema):
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

        if 'min_quantity' in data and 'max_quantity' in data:
            if data['min_quantity'] >= data['max_quantity']:
                raise UnprocessableEntity({'pointer': '/data/attributes/min-quantity'},
                                          "min-quantity should be less than max-quantity")

        if 'tickets_number' in data and 'max_quantity' in data:
            if data['tickets_number'] < data['max_quantity']:
                raise UnprocessableEntity({'pointer': '/data/attributes/tickets-number'},
                                          "tickets-number should be greater than max-quantity")

    id = fields.Integer()
    code = fields.Str(required=True)
    discount_url = fields.Url(allow_none=True)
    value = fields.Float(required=True)
    type = fields.Str(validate=validate.OneOf(choices=["amount", "percent"]), required=True)
    is_active = fields.Boolean()
    tickets_number = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    min_quantity = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    max_quantity = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    valid_from = fields.DateTime(allow_none=True)
    valid_till = fields.DateTime(allow_none=True)
    tickets = fields.Str(validate=validate.OneOf(choices=["event", "ticket"]), allow_none=True)
    created_at = fields.DateTime(allow_none=True)
    used_for = fields.Str(required=True)
    event = Relationship(attribute='event',
                         self_view='v1.discount_code_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'discount_code_id': '<id>'},
                         schema='EventSchema',
                         type_='event')
    marketer = Relationship(attribute='user',
                            self_view='v1.discount_code_user',
                            self_view_kwargs={'id': '<id>'},
                            related_view='v1.user_detail',
                            related_view_kwargs={'discount_code_id': '<id>'},
                            schema='UserSchema',
                            type_='user')


class DiscountCodeSchemaEvent(Schema):
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

        if 'min_quantity' in data and 'max_quantity' in data:
            if data['min_quantity'] >= data['max_quantity']:
                raise UnprocessableEntity({'pointer': '/data/attributes/min-quantity'},
                                          "min-quantity should be less than max-quantity")

        if 'tickets_number' in data and 'max_quantity' in data:
            if data['tickets_number'] < data['max_quantity']:
                raise UnprocessableEntity({'pointer': '/data/attributes/tickets-number'},
                                          "tickets-number should be greater than max-quantity")

    id = fields.Integer()
    code = fields.Str(required=True)
    discount_url = fields.Url(allow_none=True)
    value = fields.Float(required=True)
    type = fields.Str(validate=validate.OneOf(choices=["amount", "percent"]), required=True)
    is_active = fields.Boolean()
    tickets_number = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    min_quantity = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    max_quantity = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    valid_from = fields.DateTime(allow_none=True)
    valid_till = fields.DateTime(allow_none=True)
    tickets = fields.Str(validate=validate.OneOf(choices=["event", "ticket"]), allow_none=True)
    created_at = fields.DateTime(allow_none=True)
    used_for = fields.Str(required=True)
    event = Relationship(attribute='event',
                         self_view='v1.discount_code_events',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_list',
                         related_view_kwargs={'discount_code_id': '<id>'},
                         schema='EventSchema',
                         type_='event')


class DiscountCodeListPost(ResourceList):
    """
    Create Discount Codes
    """

    def before_post(self, args, kwargs, data):
        require_relationship(['event'], data)
        if not has_access('is_coorganizer', event_id=data['event']):
            raise ForbiddenException({'source': ''}, 'You are not authorized')

        if data['used_for'] == 'ticket':
            self.schema = DiscountCodeSchemaTicket
        elif data['used_for'] == 'event' and has_access('is_admin'):
            self.schema = DiscountCodeSchemaEvent
        else:
            raise UnprocessableEntity({'source': ''}, "Please check used_for and endpoint and verify your permission")

        data['user_id'] = current_identity.id

    def before_create_object(self, data, view_kwargs):
        if data['used_for'] == 'ticket':
            try:
                self.session.query(DiscountCode).filter_by(event_id=data['event']).filter_by(used_for='event').one()
            except NoResultFound:
                pass
            else:
                raise UnprocessableEntity({'parameter': 'event_id'},
                                          "Discount Code already exists for the provided Event ID")

    def before_get(self, args, kwargs):
        if has_access('is_admin'):
            self.schema = DiscountCodeSchemaEvent
        else:
            raise UnprocessableEntity({'source': ''}, "You are not authorized")

    decorators = (jwt_required,)
    schema = DiscountCodeSchemaEvent
    data_layer = {'session': db.session,
                  'model': DiscountCode,
                  'methods': {
                      'before_create_object': before_create_object}}


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
        if view_kwargs.get('user_id'):
            user = safe_query(self, User, 'id', view_kwargs['user_id'], 'user_id')
            query_ = query_.join(User).filter(User.id == user.id)

        if view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
            view_kwargs['event_id'] = event.id

        if view_kwargs.get('event_id') and has_access('is_coorganizer', event_id=view_kwargs['event_id']):
            self.schema = DiscountCodeSchemaTicket
            query_ = query_.filter_by(event_id=view_kwargs['event_id'])

        elif not view_kwargs.get('event_id') and has_access('is_admin'):
            self.schema = DiscountCodeSchemaEvent
        else:
            raise UnprocessableEntity({'source': ''}, "Please check used_for and endpoint and verify your permission")

        return query_

    decorators = (jwt_required,)
    methods = ['GET', ]
    view_kwargs = True
    schema = DiscountCodeSchemaEvent
    data_layer = {'session': db.session,
                  'model': DiscountCode,
                  'methods': {
                      'query': query}}


class DiscountCodeDetail(ResourceDetail):
    """
    Discount Code detail by id
    """

    def before_get(self, args, kwargs):
        if kwargs.get('event_identifier'):
            event = safe_query(db, Event, 'identifier', kwargs['event_identifier'], 'event_identifier')
            kwargs['event_id'] = event.id

        if kwargs.get('event_id') and has_access('is_admin'):
            event = safe_query(db, Event, 'id', kwargs['event_id'], 'event_id')
            if event.discount_code_id:
                kwargs['id'] = event.discount_code_id
            else:
                kwargs['id'] = None

        if kwargs.get('id'):
            discount = db.session.query(DiscountCode).filter_by(id=kwargs.get('id')).one()
            if not discount:
                raise ObjectNotFound({'parameter': '{id}'}, "DiscountCode:  not found")

            if discount.used_for == 'ticket' and has_access('is_coorganizer', event_id=discount.event_id):
                self.schema = DiscountCodeSchemaTicket

            elif discount.used_for == 'event' and has_access('is_admin'):
                self.schema = DiscountCodeSchemaEvent
            else:
                raise UnprocessableEntity({'source': ''},
                                          "Please check used_for and endpoint and verify your permission")

        else:
            raise UnprocessableEntity({'source': ''},
                                      "Please verify your permission. You must be admin to view event\
                                      discount code details")

    def before_get_object(self, view_kwargs):
        """
        query method for Discount Code detail
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
            view_kwargs['event_id'] = event.id

        if view_kwargs.get('event_id') and has_access('is_admin'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
            if event.discount_code_id:
                view_kwargs['id'] = event.discount_code_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('id'):
            discount = self.session.query(DiscountCode).filter_by(id=view_kwargs.get('id')).one()
            if not discount:
                raise ObjectNotFound({'parameter': '{id}'}, "DiscountCode:  not found")

            if discount.used_for == 'ticket' and has_access('is_coorganizer', event_id=discount.event_id):
                self.schema = DiscountCodeSchemaTicket

            elif discount.used_for == 'event' and has_access('is_admin'):
                self.schema = DiscountCodeSchemaEvent
            else:
                raise UnprocessableEntity({'source': ''},
                                          "Please check used_for and endpoint and verify your permission")

        else:
            raise UnprocessableEntity({'source': ''},
                                      "Please verify your permission. You must be admin to view event\
                                      discount code details")

    def before_update_object(self, discount, data, view_kwargs):
        """
        Method to edit object
        :param discount:
        :param data:
        :param view_kwargs:
        :return:
        """
        if 'used_for' in data:
            used_for = data['used_for']
        else:
            used_for = discount.used_for

        if discount.used_for == 'ticket' and has_access('is_coorganizer', event_id=view_kwargs.get('event_id')) \
           and used_for != 'event':
            self.schema = DiscountCodeSchemaTicket

        elif discount.used_for == 'event' and has_access('is_admin') and used_for != 'ticket':
            self.schema = DiscountCodeSchemaEvent
        else:
            raise UnprocessableEntity({'source': ''}, "Please check used_for and endpoint and verify your permission")

    def before_delete_object(self, discount, view_kwargs):
        """
        Method for Discount Code delete
        :param discount:
        :param view_kwargs:
        :return:
        """
        if discount.used_for == 'ticket' and has_access('is_coorganizer', event_id=view_kwargs['event_id']):
            self.schema = DiscountCodeSchemaTicket

        elif discount.used_for == 'event' and has_access('is_admin'):
            self.schema = DiscountCodeSchemaEvent
        else:
            raise UnprocessableEntity({'source': ''}, "Please check used_for and endpoint and verify your permission")

    decorators = (jwt_required,)
    schema = DiscountCodeSchemaEvent
    data_layer = {'session': db.session,
                  'model': DiscountCode,
                  'methods': {
                      'before_get_object': before_get_object,
                      'before_update_object': before_update_object}}


class DiscountCodeRelationshipRequired(ResourceRelationship):
    """
    Discount Code Relationship for required entities
    """

    def before_get(self, args, kwargs):
        """
        Method for get relationship
        :param args:
        :param kwargs:
        :return:
        """
        discount = db.session.query(DiscountCode).filter_by(id=kwargs.get('id')).one()
        if not discount:
            raise ObjectNotFound({'parameter': '{id}'}, "DiscountCode:  not found")
        if discount.used_for == 'ticket' and has_access('is_coorganizer', event_id=discount.event_id):
            self.schema = DiscountCodeSchemaTicket

        elif discount.used_for == 'event' and has_access('is_admin'):
            self.schema = DiscountCodeSchemaEvent
        else:
            raise UnprocessableEntity({'source': ''},
                                      "Please check used_for and endpoint and verify your permission")

    methods = ['GET', 'PATCH']
    decorators = (jwt_required,)
    schema = DiscountCodeSchemaTicket
    data_layer = {'session': db.session,
                  'model': DiscountCode}


class DiscountCodeRelationshipOptional(ResourceRelationship):
    """
    Discount Code Relationship
    """

    def before_get(self, args, kwargs):
        """
        Method for get relationship
        :param args:
        :param kwargs:
        :return:
        """
        discount = db.session.query(DiscountCode).filter_by(id=kwargs.get('id')).one()
        if not discount:
            raise ObjectNotFound({'parameter': '{id}'}, "DiscountCode:  not found")

        if discount.used_for == 'ticket' and has_access('is_coorganizer', event_id=discount.event_id):
            self.schema = DiscountCodeSchemaTicket

        elif discount.used_for == 'event' and has_access('is_admin'):
            self.schema = DiscountCodeSchemaEvent
        else:
            raise UnprocessableEntity({'source': ''},
                                      "Please check used_for and endpoint and verify your permission")

    decorators = (jwt_required,)
    schema = DiscountCodeSchemaEvent
    data_layer = {'session': db.session,
                  'model': DiscountCode}
