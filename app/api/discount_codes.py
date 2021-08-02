from datetime import datetime

from flask_jwt_extended import current_user
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound
from pytz import timezone
from sqlalchemy.orm.exc import NoResultFound

from app.api.helpers.db import get_count, safe_query, safe_query_kwargs
from app.api.helpers.errors import (
    ConflictError,
    ForbiddenError,
    MethodNotAllowed,
    UnprocessableEntityError,
)
from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required
from app.api.helpers.utilities import require_relationship
from app.api.schema.discount_codes import (
    DiscountCodeSchemaEvent,
    DiscountCodeSchemaPublic,
    DiscountCodeSchemaTicket,
)
from app.models import db
from app.models.discount_code import DiscountCode
from app.models.event import Event
from app.models.event_invoice import EventInvoice
from app.models.ticket import Ticket
from app.models.user import User


class DiscountCodeListPost(ResourceList):
    """
    Create Event and Ticket Discount code and Get Event Discount Codes
    """

    def decide_schema(self, json_data):
        """To decide discount code schema based on posted data.
        :param json_data:
        :return:"""

        used_for = json_data['data']['attributes'].get('used-for')
        if used_for in ('event', 'ticket'):
            if used_for == 'event':
                self.schema = DiscountCodeSchemaEvent
            elif used_for == 'ticket':
                self.schema = DiscountCodeSchemaTicket
        else:
            raise ConflictError(
                {'pointer': '/data/attributes/used-for'},
                "used-for attribute is required and should be equal to 'ticket' or 'event' to create discount code",
            )

    def before_post(self, args, kwargs, data):
        """Before post method to check required relationships and set user_id
        :param args:
        :param kwargs:
        :param data:
        :return:"""
        if data['used_for'] == 'ticket':
            require_relationship(['event'], data)
            if not has_access('is_coorganizer', event_id=data['event']):
                raise ForbiddenError({'source': ''}, 'You are not authorized')
        elif (
            data['used_for'] == 'event'
            and not has_access('is_admin')
            and 'events' in data
        ):
            raise UnprocessableEntityError(
                {'source': ''}, "Please verify your permission or check your relationship"
            )

        data['marketer_id'] = current_user.id

    def before_create_object(self, data, view_kwargs):
        if data.get('used_for') == 'ticket' and (event_id := data.get('event')):
            discount_codes = DiscountCode.query.filter_by(
                event_id=event_id, code=data['code'], deleted_at=None
            )
            if get_count(discount_codes) > 0:
                raise ConflictError(
                    {'pointer': '/data/attributes/code'}, 'Discount Code already exists'
                )

        if data['used_for'] == 'event':
            self.resource.schema = DiscountCodeSchemaEvent
            if 'events' in data:
                for event in data['events']:
                    try:
                        event_now = (
                            db.session.query(Event)
                            .filter_by(id=event, deleted_at=None)
                            .one()
                        )
                    except NoResultFound:
                        raise UnprocessableEntityError(
                            {'event_id': event}, "Event does not exist"
                        )
                    if event_now.discount_code_id:
                        raise UnprocessableEntityError(
                            {'event_id': event},
                            "A Discount Code already exists for the provided Event ID",
                        )
        else:
            self.resource.schema = DiscountCodeSchemaTicket

    def after_create_object(self, discount, data, view_kwargs):
        if data['used_for'] == 'event' and 'events' in data:
            for event_id in data['events']:
                event = safe_query(Event, 'id', event_id, 'event_id')
                event.discount_code_id = discount.id

    def before_get(self, args, kwargs):
        if has_access('is_admin'):
            self.schema = DiscountCodeSchemaEvent
        else:
            raise UnprocessableEntityError({'source': ''}, "You are not authorized")

    decorators = (jwt_required,)
    schema = DiscountCodeSchemaTicket
    data_layer = {
        'session': db.session,
        'model': DiscountCode,
        'methods': {
            'before_create_object': before_create_object,
            'after_create_object': after_create_object,
        },
    }


class DiscountCodeList(ResourceList):
    """
    Get the list of Ticket Discount Code
    """

    def query(self, view_kwargs):
        """
        query method for Discount Code List
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(DiscountCode)
        # user can only access his/her discount codes.
        if view_kwargs.get('user_id'):
            if has_access('is_user_itself', user_id=view_kwargs['user_id']):
                user = safe_query_kwargs(User, view_kwargs, 'user_id')
                query_ = query_.join(User).filter(User.id == user.id)
            else:
                raise ForbiddenError({'source': ''}, 'You are not authorized')

        if view_kwargs.get('event_identifier'):
            event = safe_query_kwargs(
                Event,
                view_kwargs,
                'event_identifier',
                'identifier',
            )
            view_kwargs['event_id'] = event.id

        # event co-organizer access required for discount codes under an event.
        if view_kwargs.get('event_id'):
            if has_access('is_coorganizer', event_id=view_kwargs['event_id']):
                self.schema = DiscountCodeSchemaTicket
                query_ = query_.filter_by(event_id=view_kwargs['event_id'])
            else:
                raise ForbiddenError({'source': ''}, 'Event organizer access required')

        # discount_code - ticket :: many-to-many relationship
        if view_kwargs.get('ticket_id'):
            ticket = safe_query_kwargs(Ticket, view_kwargs, 'ticket_id')
            if not has_access('is_coorganizer', event_id=ticket.event_id):
                raise ForbiddenError({'source': ''}, 'Event organizer access required')
            self.schema = DiscountCodeSchemaTicket
            query_ = query_.filter(DiscountCode.tickets.any(id=ticket.id))

        return query_

    decorators = (jwt_required,)
    methods = [
        'GET',
    ]
    view_kwargs = True
    schema = DiscountCodeSchemaPublic
    data_layer = {
        'session': db.session,
        'model': DiscountCode,
        'methods': {'query': query},
    }


class DiscountCodeDetail(ResourceDetail):
    """
    Discount Code detail by id or code.
    """

    def decide_schema(self, json_data):
        """To decide discount code schema based on posted data.
        :param json_data:
        :return:"""

        used_for = json_data['data']['attributes'].get('used-for')
        try:
            discount = (
                db.session.query(DiscountCode)
                .filter_by(id=int(json_data['data']['id']))
                .one()
            )
        except NoResultFound:
            raise ObjectNotFound({'parameter': '{id}'}, "DiscountCode: not found")

        if not used_for:
            used_for = discount.used_for
        elif used_for != discount.used_for:
            raise ConflictError(
                {'pointer': '/data/attributes/used-for'},
                "Cannot modify discount code usage type",
            )

        if used_for == 'ticket':
            self.schema = DiscountCodeSchemaTicket
        elif used_for == 'event':
            self.schema = DiscountCodeSchemaEvent

    def before_get(self, args, kwargs):
        if kwargs.get('ticket_id'):
            if has_access('is_coorganizer'):
                ticket = safe_query_kwargs(Ticket, kwargs, 'ticket_id')
                if ticket.discount_code_id:
                    kwargs['id'] = ticket.discount_code_id
                else:
                    kwargs['id'] = None
            else:
                raise UnprocessableEntityError(
                    {'source': ''},
                    "Please verify your permission. You must have coorganizer "
                    "privileges to view ticket discount code details",
                )
        if kwargs.get('event_id'):
            if has_access('is_admin'):
                event = safe_query_kwargs(Event, kwargs, 'event_id')
                if event.discount_code_id:
                    kwargs['id'] = event.discount_code_id
                else:
                    kwargs['id'] = None
            else:
                raise UnprocessableEntityError(
                    {'source': ''},
                    "Please verify your permission. You must be admin to view event discount code details",
                )

        if kwargs.get('event_identifier'):
            event = safe_query_kwargs(Event, kwargs, 'event_identifier', 'identifier')
            kwargs['event_id'] = event.id

        if kwargs.get('discount_event_identifier'):
            event = safe_query(
                Event,
                'identifier',
                kwargs['discount_event_identifier'],
                'event_identifier',
            )
            kwargs['discount_event_id'] = event.id

        if kwargs.get('event_id') and has_access('is_admin'):
            event = safe_query_kwargs(Event, kwargs, 'event_id')
            if event.discount_code_id:
                kwargs['id'] = event.discount_code_id
            else:
                kwargs['id'] = None

        # Any registered user can fetch discount code details using the code.
        if kwargs.get('code'):
            # filter on deleted_at is required to catch the id of a
            # discount code which has not been deleted.
            discount = (
                db.session.query(DiscountCode)
                .filter_by(
                    code=kwargs.get('code'),
                    event_id=kwargs.get('discount_event_id'),
                    deleted_at=None,
                )
                .first()
            )
            if discount:
                kwargs['id'] = discount.id
                if discount.valid_from:
                    discount_tz = discount.valid_from.tzinfo
                current_time = datetime.now().replace(
                    tzinfo=discount_tz or timezone('UTC')
                )
                if not discount.is_active:
                    raise MethodNotAllowed(
                        {'parameter': '{code}'}, "Discount Code is not active"
                    )
                if (
                    current_time < discount.valid_from
                    or current_time > discount.valid_expire_time
                ):
                    raise MethodNotAllowed(
                        {'parameter': '{code}'},
                        "Discount Code is not active in current time frame",
                    )
            else:
                raise ObjectNotFound({'parameter': '{code}'}, "DiscountCode: not found")

            self.schema = DiscountCodeSchemaTicket
            return

        if kwargs.get('id'):
            try:
                discount = (
                    db.session.query(DiscountCode).filter_by(id=kwargs.get('id')).one()
                )
            except NoResultFound:
                raise ObjectNotFound({'parameter': '{id}'}, "DiscountCode: not found")

            #             if discount.used_for == 'ticket' and has_access('is_coorganizer', event_id=discount.event_id):
            if discount.used_for == 'ticket':
                self.schema = DiscountCodeSchemaTicket

            #             elif discount.used_for == 'event' and has_access('is_admin'):
            elif discount.used_for == 'event':
                self.schema = DiscountCodeSchemaEvent
            else:
                raise UnprocessableEntityError(
                    {'source': ''}, "Please verify your permission"
                )

    def before_get_object(self, view_kwargs):
        """
        before get method for Discount Code detail
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('event_identifier'):
            event = safe_query_kwargs(
                Event,
                view_kwargs,
                'event_identifier',
                'identifier',
            )
            view_kwargs['event_id'] = event.id

        if view_kwargs.get('event_id') and has_access('is_admin'):
            event = safe_query_kwargs(Event, view_kwargs, 'event_id')
            if event.discount_code_id:
                view_kwargs['id'] = event.discount_code_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('event_invoice_id') and has_access('is_admin'):
            event_invoice = safe_query_kwargs(
                EventInvoice,
                view_kwargs,
                'event_invoice_id',
            )
            if event_invoice.discount_code_id:
                view_kwargs['id'] = event_invoice.discount_code_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('event_invoice_identifier') and has_access('is_admin'):
            event_invoice = safe_query_kwargs(
                EventInvoice, view_kwargs, 'event_invoice_identifier', 'identifier'
            )
            if event_invoice.discount_code_id:
                view_kwargs['id'] = event_invoice.discount_code_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('id'):
            try:
                discount = (
                    self.session.query(DiscountCode)
                    .filter_by(id=view_kwargs.get('id'))
                    .one()
                )
            except NoResultFound:
                raise ObjectNotFound({'parameter': '{id}'}, "DiscountCode: not found")

            if 'code' in view_kwargs:  # usage via discount code is public
                self.schema = DiscountCodeSchemaPublic
                return

            #             if discount.used_for == 'ticket' and has_access('is_coorganizer', event_id=discount.event_id):
            if discount.used_for == 'ticket':
                self.schema = DiscountCodeSchemaTicket

            #             elif discount.used_for == 'event' and has_access('is_admin'):
            elif discount.used_for == 'event':
                self.schema = DiscountCodeSchemaEvent
            else:
                raise UnprocessableEntityError(
                    {'source': ''}, "Please verify your permission"
                )

        elif not view_kwargs.get('id') and not has_access('is_admin'):
            raise UnprocessableEntityError(
                {'source': ''},
                "Please verify your permission. You must be admin to view event\
                                      discount code details",
            )

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
        if (
            discount.used_for == 'ticket'
            and has_access('is_coorganizer', event_id=view_kwargs.get('event_id'))
            and used_for != 'event'
        ):
            self.schema = DiscountCodeSchemaTicket
            self.resource.schema = DiscountCodeSchemaTicket

        elif (
            discount.used_for == 'event'
            and has_access('is_admin')
            and used_for != 'ticket'
        ):
            self.schema = DiscountCodeSchemaEvent
            self.resource.schema = DiscountCodeSchemaEvent
        else:
            raise UnprocessableEntityError(
                {'source': ''}, "Please verify your permission"
            )

    def before_delete_object(self, discount, view_kwargs):
        """
        Method for Discount Code delete
        :param discount:
        :param view_kwargs:
        :return:
        """
        if discount.used_for == 'ticket' and has_access(
            'is_coorganizer', event_id=view_kwargs['event_id']
        ):
            self.schema = DiscountCodeSchemaTicket

        elif discount.used_for == 'event' and has_access('is_admin'):
            self.schema = DiscountCodeSchemaEvent
        else:
            raise UnprocessableEntityError(
                {'source': ''}, "Please verify your permission"
            )

    #     decorators = (jwt_required,)
    schema = DiscountCodeSchemaTicket
    data_layer = {
        'session': db.session,
        'model': DiscountCode,
        'methods': {
            'before_get_object': before_get_object,
            'before_update_object': before_update_object,
            'before_delete_object': before_delete_object,
        },
    }


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
        try:
            discount = db.session.query(DiscountCode).filter_by(id=kwargs.get('id')).one()
        except NoResultFound:
            raise ObjectNotFound({'parameter': '{id}'}, "DiscountCode: not found")
        if discount.used_for == 'ticket' and has_access(
            'is_coorganizer', event_id=discount.event_id
        ):
            self.schema = DiscountCodeSchemaTicket

        elif discount.used_for == 'event' and has_access('is_admin'):
            self.schema = DiscountCodeSchemaEvent
        else:
            raise UnprocessableEntityError(
                {'source': ''}, "Please verify your permission"
            )

    methods = ['GET', 'PATCH']
    decorators = (jwt_required,)
    schema = DiscountCodeSchemaTicket
    data_layer = {'session': db.session, 'model': DiscountCode}


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
        try:
            discount = db.session.query(DiscountCode).filter_by(id=kwargs.get('id')).one()
        except NoResultFound:
            raise ObjectNotFound({'parameter': '{id}'}, "DiscountCode: not found")

        if discount.used_for == 'ticket' and has_access(
            'is_coorganizer', event_id=discount.event_id
        ):
            self.schema = DiscountCodeSchemaTicket

        elif discount.used_for == 'event' and has_access('is_admin'):
            self.schema = DiscountCodeSchemaEvent
        else:
            raise UnprocessableEntityError(
                {'source': ''}, "Please verify your permission"
            )

    schema = DiscountCodeSchemaEvent
    data_layer = {'session': db.session, 'model': DiscountCode}
