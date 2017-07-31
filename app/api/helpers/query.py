from flask import request
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.helpers.db import safe_query
from app.models.event import Event
from app.api.helpers.permission_manager import has_access


def event_query(self, query_, view_kwargs, event_id, event_identifier, permission):
    """
    Queries the event according to 'event_id' and 'event_identifier' and joins for the query
    For draft events, if the user is not logged in or does not have required permissions, a 404 is raised
    :param self:
    :param event_id: String representing event_id in the view_kwargs
    :param event_identifier: String representing event_identifier in the view_kwargs
    :param query_: Query object
    :param view_kwargs: view_kwargs from the API
    :param permission: the name of the permission to be applied as a string
    :return:
    """
    if view_kwargs.get(event_id):
        event = safe_query(self, Event, 'id', view_kwargs[event_id], event_id)
        if event.state != 'published':
            if 'Authorization' in request.headers and has_access(permission, event_id=event.id):
                query_ = query_.join(Event).filter(Event.id == event.id)
            else:
                raise ObjectNotFound({'parameter': event_id},
                                     "Event: {} not found".format(view_kwargs[event_id]))
        else:
            query_ = query_.join(Event).filter(Event.id == event.id)
    elif view_kwargs.get(event_identifier):
        event = safe_query(self, Event, 'identifier', view_kwargs[event_identifier], event_identifier)
        if event.state != 'published':
            if 'Authorization' in request.headers and has_access(permission, event_id=event.id):
                query_ = query_.join(Event).filter(Event.id == event.id)
            else:
                raise ObjectNotFound({'parameter': event_identifier},
                                     "Event: {} not found".format(view_kwargs[event_identifier]))
        else:
            query_ = query_.join(Event).filter(Event.id == event.id)
    return query_
