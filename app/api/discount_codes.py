from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound
from sqlalchemy.orm.exc import NoResultFound

from app.api.helpers.db import safe_query
from app.api.helpers.exceptions import UnprocessableEntity, ForbiddenException
from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required, current_identity
from app.api.helpers.utilities import require_relationship
from app.api.schema.discount_codes import DiscountCodeSchemaTicket, DiscountCodeSchemaEvent
from app.models import db
from app.models.discount_code import DiscountCode
from app.models.event import Event
from app.models.event_invoice import EventInvoice
from app.models.user import User


class DiscountCodeListPost(ResourceList):
    """
    Create Discount Codes
    """

    def before_post(self, args, kwargs, data):
        if data['used_for'] == 'ticket':
            self.schema = DiscountCodeSchemaTicket
            require_relationship(['event'], data)
            if not has_access('is_coorganizer', event_id=data['event']):
                raise ForbiddenException({'source': ''}, 'You are not authorized')
        elif data['used_for'] == 'event' and has_access('is_admin') and 'events' in data:
            self.schema = DiscountCodeSchemaEvent
        else:
            raise UnprocessableEntity({'source': ''}, "Please verify your permission or check your relationship")

        data['user_id'] = current_identity.id

    def before_create_object(self, data, view_kwargs):
        if data['used_for'] == 'event' and 'events' in data:
            for event in data['events']:
                try:
                    event_now = db.session.query(Event).filter_by(id=event).one()
                except NoResultFound:
                    raise UnprocessableEntity({'event_id': event},
                                              "Event does not exist")
                if event_now.discount_code_id:
                    raise UnprocessableEntity({'event_id': event},
                                              "A Discount Code already exists for the provided Event ID")

    def after_create_object(self, discount, data, view_kwargs):
        if data['used_for'] == 'event' and 'events' in data:
            for event_id in data['events']:
                event = safe_query(self, Event, 'id', event_id, 'event_id')
                event.discount_code_id = discount.id

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
                      'before_create_object': before_create_object,
                      'after_create_object': after_create_object}}


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

        return query_

    decorators = (jwt_required,)
    methods = ['GET', ]
    view_kwargs = True
    schema = DiscountCodeSchemaTicket
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
                                          "Please verify your permission")

        elif not kwargs.get('id') and not has_access('is_admin'):
            raise UnprocessableEntity({'source': ''},
                                      "Please verify your permission. You must be admin to view event\
                                      discount code details")

    def before_get_object(self, view_kwargs):
        """
        before get method for Discount Code detail
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

        if view_kwargs.get('event_invoice_id') and has_access('is_admin'):
            event_invoice = safe_query(self, EventInvoice, 'id', view_kwargs['event_invoice_id'], 'event_invoice_id')
            if event_invoice.discount_code_id:
                view_kwargs['id'] = event_invoice.discount_code_id
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
                                          "Please verify your permission")

        elif not view_kwargs.get('id') and not has_access('is_admin'):
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
            raise UnprocessableEntity({'source': ''}, "Please verify your permission")

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
            raise UnprocessableEntity({'source': ''}, "Please verify your permission")

    decorators = (jwt_required,)
    schema = DiscountCodeSchemaEvent
    data_layer = {'session': db.session,
                  'model': DiscountCode,
                  'methods': {
                      'before_get_object': before_get_object,
                      'before_update_object': before_update_object,
                      'before_delete_object': before_delete_object}}


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
                                      "Please verify your permission")

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
                                      "Please verify your permission")

    decorators = (jwt_required,)
    schema = DiscountCodeSchemaEvent
    data_layer = {'session': db.session,
                  'model': DiscountCode}
