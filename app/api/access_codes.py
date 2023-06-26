from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound
from sqlalchemy.orm.exc import NoResultFound

from app.api.bootstrap import api
from app.api.helpers.db import safe_query, safe_query_kwargs
from app.api.helpers.errors import ConflictError, ForbiddenError, UnprocessableEntityError
from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required
from app.api.helpers.query import event_query
from app.api.helpers.utilities import require_relationship
from app.api.schema.access_codes import AccessCodeSchema
from app.models import db
from app.models.access_code import AccessCode
from app.models.event import Event
from app.models.ticket import Ticket
from app.models.user import User


class AccessCodeListPost(ResourceList):
    """
    Create AccessCodes
    """

    def before_post(self, args, kwargs, data):
        """
        before post method to check for required relationships and permissions
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['event', 'user'], data)
        if not has_access('is_coorganizer', event_id=data['event']):
            raise ForbiddenError({'source': ''}, "Minimum Organizer access required")

    def before_create_object(self, data, view_kwargs):
        """
        before create object method for AccessCodeListPost Class
        :param data:
        :param view_kwargs:
        :return:
        """
        if data.get('tickets', None):
            for ticket in data['tickets']:
                # Ensuring that the ticket exists and is hidden.
                try:
                    ticket_object = (
                        self.session.query(Ticket)
                        .filter_by(id=int(ticket), deleted_at=None)
                        .one()
                    )
                    if not ticket_object.is_hidden:
                        raise ConflictError(
                            {'pointer': '/data/relationships/tickets'},
                            f"Ticket with id {ticket} is public."
                            + " Access code cannot be applied to public tickets",
                        )
                except NoResultFound:
                    raise ConflictError(
                        {'pointer': '/data/relationships/tickets'},
                        f"Ticket with id {str(ticket)} does not exists",
                    )

    schema = AccessCodeSchema
    methods = [
        'POST',
    ]
    data_layer = {
        'session': db.session,
        'model': AccessCode,
        'methods': {'before_create_object': before_create_object},
    }


class AccessCodeList(ResourceList):
    """
    List AccessCodes
    """

    def query(self, view_kwargs):
        """
        Method to get access codes list based on different view_kwargs
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(AccessCode)
        query_ = event_query(query_, view_kwargs, restrict=True)
        if view_kwargs.get('user_id'):
            user = safe_query_kwargs(User, view_kwargs, 'user_id')
            if not has_access('is_user_itself', user_id=user.id):
                raise ForbiddenError({'source': ''}, 'Access Forbidden')
            query_ = query_.join(User).filter(User.id == user.id)
        if view_kwargs.get('ticket_id'):
            ticket = safe_query_kwargs(Ticket, view_kwargs, 'ticket_id')
            if not has_access('is_coorganizer', event_id=ticket.event_id):
                raise ForbiddenError({'source': ''}, 'Access Forbidden')
            # access_code - ticket :: many-to-many relationship
            query_ = AccessCode.query.filter(AccessCode.tickets.any(id=ticket.id))
            query_
        return query_

    view_kwargs = True
    methods = [
        'GET',
    ]
    schema = AccessCodeSchema
    data_layer = {
        'session': db.session,
        'model': AccessCode,
        'methods': {
            'query': query,
        },
    }


class AccessCodeDetail(ResourceDetail):
    """
    AccessCode detail by id or code
    """

    def before_get(self, args, kwargs):
        """
        before get method of access code details.
        Check for permissions on the basis of kwargs.
        :param args:
        :param kwargs:
        :return:
        """
        # Any user can fetch access code details using the code.

        if kwargs.get('access_event_identifier'):
            event = safe_query(
                Event,
                'identifier',
                kwargs['access_event_identifier'],
                'event_identifier',
            )
            kwargs['access_event_id'] = event.id
        if kwargs.get('code') and kwargs.get('access_event_id'):
            access = (
                db.session.query(AccessCode)
                .filter_by(
                    code=kwargs.get('code'), event_id=kwargs.get('access_event_id')
                )
                .first()
            )
            if access:
                kwargs['id'] = access.id
            else:
                raise ObjectNotFound({'parameter': '{code}'}, "Access Code:  not found")
            return

        # Co-organizer or the admin can fetch access code details using the id.
        if kwargs.get('id'):
            access = db.session.query(AccessCode).filter_by(id=kwargs.get('id')).one()
            if not access:
                raise ObjectNotFound({'parameter': '{id}'}, "Access Code:  not found")

            if not has_access('is_coorganizer', event_id=access.event_id):
                raise UnprocessableEntityError(
                    {'source': ''}, "Please verify your permission"
                )

    decorators = (
        api.has_permission(
            'is_coorganizer',
            fetch='event_id',
            model=AccessCode,
            methods="PATCH",
        ),
        api.has_permission(
            'is_coorganizer_but_not_admin',
            fetch='event_id',
            model=AccessCode,
            methods="DELETE",
        ),
    )
    schema = AccessCodeSchema
    data_layer = {'session': db.session, 'model': AccessCode}


class AccessCodeRelationshipRequired(ResourceRelationship):
    """
    AccessCode Relationship Required
    """

    decorators = (jwt_required,)
    methods = ['GET', 'PATCH']
    schema = AccessCodeSchema
    data_layer = {'session': db.session, 'model': AccessCode}


class AccessCodeRelationshipOptional(ResourceRelationship):
    """
    AccessCode Relationship Optional
    """

    decorators = (jwt_required,)
    schema = AccessCodeSchema
    data_layer = {'session': db.session, 'model': AccessCode}
