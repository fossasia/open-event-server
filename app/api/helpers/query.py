import datetime

from flask import request
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.helpers.db import safe_query_kwargs
from app.api.helpers.permission_manager import has_access
from app.models.event import Event
from app.models.role import Role
from app.models.users_events_role import UsersEventsRoles


def event_query(
    query_,
    view_kwargs,
    event_id='event_id',
    event_identifier='event_identifier',
    permission='is_coorganizer_endpoint_related_to_event',
):
    """
    Queries the event according to 'event_id' and 'event_identifier' and joins for the query
    For draft events, if the user is not logged in or does not have required permissions, a 404 is raised
    :param event_id: String representing event_id in the view_kwargs
    :param event_identifier: String representing event_identifier in the view_kwargs
    :param query_: Query object
    :param view_kwargs: view_kwargs from the API
    :param permission: the name of the permission to be applied as a string. Default: is_coorganizer
    :return:
    """
    if view_kwargs.get(event_id):
        event = safe_query_kwargs(Event, view_kwargs, event_id)
        if event.state != 'published' and (
            'Authorization' not in request.headers
            or not has_access(permission, event_id=event.id)
        ):
            raise ObjectNotFound(
                {'parameter': event_id},
                "Event: {} not found".format(view_kwargs[event_id]),
            )
        query_ = query_.join(Event).filter(Event.id == event.id)
    elif view_kwargs.get(event_identifier):
        event = safe_query_kwargs(Event, view_kwargs, event_identifier, 'identifier')
        if event.state != 'published' and (
            'Authorization' not in request.headers
            or not has_access(permission, event_id=event.id)
        ):
            raise ObjectNotFound(
                {'parameter': event_identifier},
                "Event: {} not found".format(view_kwargs[event_identifier]),
            )
        query_ = query_.join(Event).filter(Event.id == event.id)
    return query_


def get_user_event_roles_by_role_name(event_id, role_name):
    role = Role.query.filter_by(name=role_name).first()
    return UsersEventsRoles.query.filter_by(event_id=event_id).filter(
        UsersEventsRoles.role == role
    )
