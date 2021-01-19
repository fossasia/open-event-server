from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.helpers.db import safe_query_kwargs
from app.api.helpers.errors import ForbiddenError
from app.api.helpers.permission_manager import has_access
from app.api.helpers.query import event_query
from app.api.helpers.utilities import require_relationship
from app.api.schema.tracks import TrackSchema
from app.models import db
from app.models.session import Session
from app.models.track import Track


class TrackListPost(ResourceList):
    """
    List and create Tracks
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
        if not has_access('is_track_organizer', event_id=data['event']):
            raise ForbiddenError({'source': ''}, 'Track-organizer access is required.')

    schema = TrackSchema
    data_layer = {'session': db.session, 'model': Track}


class TrackList(ResourceList):
    """
    List and create Tracks
    """

    def query(self, view_kwargs):
        """
        query method for resource list
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(Track)
        query_ = event_query(query_, view_kwargs)
        return query_

    view_kwargs = True
    methods = ['GET']
    schema = TrackSchema
    data_layer = {'session': db.session, 'model': Track, 'methods': {'query': query}}


class TrackDetail(ResourceDetail):
    """
    Track detail by id
    """

    def before_get_object(self, view_kwargs):
        """
        before get method to get the resource id for fetching details
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('session_id'):
            session = safe_query_kwargs(Session, view_kwargs, 'session_id')
            if session.event_id:
                view_kwargs['id'] = session.track_id
            else:
                view_kwargs['id'] = None

    decorators = (
        api.has_permission(
            'is_track_organizer',
            fetch='event_id',
            model=Track,
            methods="PATCH,DELETE",
        ),
    )
    schema = TrackSchema
    data_layer = {
        'session': db.session,
        'model': Track,
        'methods': {'before_get_object': before_get_object},
    }


class TrackRelationshipRequired(ResourceRelationship):
    """
    Track Relationship
    """

    decorators = (
        api.has_permission(
            'is_track_organizer',
            fetch='event_id',
            model=Track,
            methods="PATCH",
        ),
    )
    methods = ['GET', 'PATCH']
    schema = TrackSchema
    data_layer = {'session': db.session, 'model': Track}


class TrackRelationshipOptional(ResourceRelationship):
    """
    Track Relationship
    """

    decorators = (
        api.has_permission(
            'is_track_organizer',
            fetch='event_id',
            model=Track,
            methods="PATCH,DELETE",
        ),
    )
    schema = TrackSchema
    data_layer = {'session': db.session, 'model': Track}
