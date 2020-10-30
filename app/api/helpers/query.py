from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.helpers.db import safe_query_kwargs
from app.api.helpers.errors import ForbiddenError
from app.api.helpers.permission_manager import has_access, is_logged_in
from app.models.event import Event
from app.models.role import Role
from app.models.users_events_role import UsersEventsRoles


def event_query(
    query_,
    view_kwargs,
    event_id='event_id',
    event_identifier='event_identifier',
    permission=None,
    restrict=False,
):
    """
    Queries the event according to 'event_id' and 'event_identifier' and joins for the query
    For draft events, a 404 is raised
    If the user is not logged in or does not have required permissions, 403 is raised

    For a draft event, unless the user is organizer+ or has access to the passed permission,
    404 will always be raised, regardless of restrict being True or not.

    For a published event, if restrict is False, the query will allowed.

    If restrict is True, then the passed permission or co-organizer access will be enforced.
    If the permission passes, query will be allowed, otherwise, a 403 will be thrown

    :param event_id: String representing event_id in the view_kwargs
    :param event_identifier: String representing event_identifier in the view_kwargs
    :param query_: Query object
    :param view_kwargs: view_kwargs from the API
    :param permission: the name of the permission to be applied as a string. Default: is_coorganizer
    :return:
    """
    permission = permission or 'is_coorganizer_endpoint_related_to_event'

    event = None
    if view_kwargs.get(event_id):
        event = safe_query_kwargs(Event, view_kwargs, event_id)
    elif view_kwargs.get(event_identifier):
        event = safe_query_kwargs(Event, view_kwargs, event_identifier, 'identifier')

    if event:
        forbidden = not is_logged_in() or not has_access(permission, event_id=event.id)
        if event.state != 'published' and forbidden:
            raise ObjectNotFound(
                {'parameter': event_id},
                f"Event: {event.id} not found",
            )
        if restrict and forbidden:
            raise ForbiddenError(
                {'parameter': event_id},
                f"You don't have access to event {event.id}",
            )
        query_ = query_.join(Event).filter(Event.id == event.id)
    return query_


def get_user_event_roles_by_role_name(event_id, role_name):
    role = Role.query.filter_by(name=role_name).first()
    return UsersEventsRoles.query.filter_by(event_id=event_id).filter(
        UsersEventsRoles.role == role
    )
