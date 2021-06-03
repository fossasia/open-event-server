from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from sqlalchemy.orm.exc import NoResultFound

from app.api.bootstrap import api
from app.api.helpers.db import safe_query, safe_query_kwargs
from app.api.helpers.errors import ForbiddenError, UnprocessableEntityError
from app.api.helpers.permission_manager import has_access
from app.api.helpers.utilities import require_relationship
from app.api.schema.event_copyright import EventCopyrightSchema
from app.models import db
from app.models.event import Event
from app.models.event_copyright import EventCopyright


class EventCopyrightListPost(ResourceList):
    """
    Event Copyright List Post class for creating an event copyright
    Only POST method allowed
    """

    def before_post(self, args, kwargs, data):
        """
        before post method to check for required relationship and proper permission
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['event'], data)
        if not has_access('is_coorganizer', event_id=data['event']):
            raise ForbiddenError({'source': ''}, 'Co-organizer access is required.')

    def before_create_object(self, data, view_kwargs):
        """
        before create method to check if event copyright for the event already exists or not
        :param data:
        :param view_kwargs:
        :return:
        """
        try:
            self.session.query(EventCopyright).filter_by(
                event_id=data['event'], deleted_at=None
            ).one()
        except NoResultFound:
            pass
        else:
            raise UnprocessableEntityError(
                {'parameter': 'event_identifier'},
                "Event Copyright already exists for the provided Event ID",
            )

    methods = [
        'POST',
    ]
    view_kwargs = True
    schema = EventCopyrightSchema
    data_layer = {
        'session': db.session,
        'model': EventCopyright,
        'methods': {'before_create_object': before_create_object},
    }


class EventCopyrightDetail(ResourceDetail):
    """
    Event Copyright Detail Class
    """

    def before_get_object(self, view_kwargs):
        """
        before get method to get the copyright id to fetch details
        :param view_kwargs:
        :return:
        """
        event = None
        if view_kwargs.get('event_id'):
            event = safe_query_kwargs(Event, view_kwargs, 'event_id')
        elif view_kwargs.get('event_identifier'):
            event = safe_query_kwargs(
                Event, view_kwargs, 'event_identifier', 'identifier'
            )

        if event:
            event_copyright = safe_query(EventCopyright, 'event_id', event.id, 'event_id')
            view_kwargs['id'] = event_copyright.id

    decorators = (
        api.has_permission(
            'is_coorganizer',
            fetch="event_id",
            model=EventCopyright,
            methods="PATCH,DELETE",
        ),
    )
    schema = EventCopyrightSchema
    data_layer = {
        'session': db.session,
        'model': EventCopyright,
        'methods': {'before_get_object': before_get_object},
    }


class EventCopyrightRelationshipRequired(ResourceRelationship):
    """
    Event Copyright Relationship
    """

    decorators = (
        api.has_permission(
            'is_coorganizer',
            fetch="event_id",
            model=EventCopyright,
            methods="PATCH",
        ),
    )
    methods = ['GET', 'PATCH']
    schema = EventCopyrightSchema
    data_layer = {'session': db.session, 'model': EventCopyright}
