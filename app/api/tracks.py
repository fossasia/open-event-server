from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.helpers.db import safe_query
from app.api.helpers.exceptions import ForbiddenException
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
        require_relationship(['event'], data)
        if not has_access('is_track_organizer', event_id=data['event']):
            raise ForbiddenException({'source': ''}, 'Track-organizer access is required.')

    schema = TrackSchema
    data_layer = {'session': db.session,
                  'model': Track}


class TrackList(ResourceList):
    """
    List and create Tracks
    """
    def query(self, view_kwargs):
        query_ = self.session.query(Track)
        query_ = event_query(self, query_, view_kwargs)
        return query_

    view_kwargs = True
    methods = ['GET']
    schema = TrackSchema
    data_layer = {'session': db.session,
                  'model': Track,
                  'methods': {
                      'query': query
                  }}


class TrackDetail(ResourceDetail):
    """
    Track detail by id
    """
    def before_get_object(self, view_kwargs):
        if view_kwargs.get('session_id'):
            session = safe_query(self, Session, 'id', view_kwargs['session_id'], 'session_id')
            if session.event_id:
                view_kwargs['id'] = session.track_id
            else:
                view_kwargs['id'] = None

    decorators = (api.has_permission('is_track_organizer', fetch='event_id',
                  fetch_as="event_id", model=Track, methods="PATCH,DELETE"), )
    schema = TrackSchema
    data_layer = {'session': db.session,
                  'model': Track,
                  'methods': {'before_get_object': before_get_object}}


class TrackRelationshipRequired(ResourceRelationship):
    """
    Track Relationship
    """
    decorators = (api.has_permission('is_track_organizer', fetch='event_id',
                                     fetch_as="event_id", model=Track, methods="PATCH"),)
    methods = ['GET', 'PATCH']
    schema = TrackSchema
    data_layer = {'session': db.session,
                  'model': Track}


class TrackRelationshipOptional(ResourceRelationship):
    """
    Track Relationship
    """
    decorators = (api.has_permission('is_track_organizer', fetch='event_id',
                                     fetch_as="event_id", model=Track, methods="PATCH,DELETE",),)
    schema = TrackSchema
    data_layer = {'session': db.session,
                  'model': Track}
