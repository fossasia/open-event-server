import re

from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from marshmallow import pre_load, validates_schema

from app.api.bootstrap import api
from app.api.helpers.utilities import dasherize
from app.api.helpers.permissions import jwt_required
from app.models import db
from app.models.track import Track
from app.models.session import Session
from app.api.helpers.exceptions import UnprocessableEntity
from app.models.event import Event
from app.api.helpers.db import safe_query
from app.api.helpers.utilities import require_relationship
from app.api.helpers.exceptions import ForbiddenException
from app.api.helpers.permission_manager import has_access


class TrackSchema(Schema):
    """
    Api Schema for track model
    """

    class Meta:
        """
        Meta class for User Api Schema
        """
        type_ = 'track'
        self_view = 'v1.track_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    @pre_load
    def remove_font_color(self, data):
        if data.get('font_color'):
            del data['font_color']
        return data

    @validates_schema
    def valid_color(self, data):
        if not re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', data['color']):
            return UnprocessableEntity({'pointer': 'data/attributes/color'}, "Color should be proper HEX color code")

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    color = fields.Str(required=True)
    font_color = fields.Str(allow_none=True)
    event = Relationship(attribute='event',
                         self_view='v1.track_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'track_id': '<id>'},
                         schema='EventSchema',
                         type_='event')
    sessions = Relationship(attribute='sessions',
                            self_view='v1.track_sessions',
                            self_view_kwargs={'id': '<id>'},
                            related_view='v1.session_list',
                            related_view_kwargs={'track_id': '<id>'},
                            schema='SessionSchema',
                            many=True,
                            type_='session')


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
        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
            query_ = query_.join(Event).filter(Event.id == event.id)
        elif view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
            query_ = query_.join(Event).filter(Event.id == event.id)
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
                  fetch_as="event_id", model=Track, methods="PATCH,DELETE",
                  check=lambda a: a.get('id') is not None), )
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
