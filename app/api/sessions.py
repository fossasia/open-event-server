from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from marshmallow import validates_schema
import marshmallow.validate as validate

from app.api.bootstrap import api
from app.api.events import Event
from app.api.helpers.utilities import dasherize
from app.models import db
from app.models.session import Session
from app.models.track import Track
from app.models.session_type import SessionType
from app.models.microlocation import Microlocation
from app.api.helpers.exceptions import UnprocessableEntity
from app.api.helpers.db import safe_query


class SessionSchema(Schema):
    """
    Api schema for Session Model
    """

    class Meta:
        """
        Meta class for Session Api Schema
        """
        type_ = 'session'
        self_view = 'v1.session_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    @validates_schema(pass_original=True)
    def validate_date(self, data, original_data):
        if 'id' in original_data['data']:
            session = Session.query.filter_by(id=original_data['data']['id']).one()

            if 'starts_at' not in data:
                data['starts_at'] = session.starts_at

            if 'ends_at' not in data:
                data['ends_at'] = session.ends_at

        if data['starts_at'] >= data['ends_at']:
            raise UnprocessableEntity({'pointer': '/data/attributes/ends-at'}, "ends-at should be after starts-at")

    id = fields.Str(dump_only=True)
    title = fields.Str(required=True)
    subtitle = fields.Str(allow_none=True)
    level = fields.Int(allow_none=True)
    short_abstract = fields.Str(allow_none=True)
    long_abstract = fields.Str(allow_none=True)
    comments = fields.Str(allow_none=True)
    starts_at = fields.DateTime(required=True)
    ends_at = fields.DateTime(required=True)
    language = fields.Str(allow_none=True)
    slides_url = fields.Url(allow_none=True)
    video_url = fields.Url(allow_none=True)
    audio_url = fields.Url(allow_none=True)
    signup_url = fields.Url(allow_none=True)
    state = fields.Str(validate=validate.OneOf(choices=["pending", "accepted", "confirmed", "rejected", "draft"]),
                       allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    deleted_at = fields.DateTime(dump_only=True)
    submitted_at = fields.DateTime(allow_none=True)
    is_mail_sent = fields.Boolean()
    microlocation = Relationship(attribute='microlocation',
                                 self_view='v1.session_microlocation',
                                 self_view_kwargs={'id': '<id>'},
                                 related_view='v1.microlocation_detail',
                                 related_view_kwargs={'session_id': '<id>'},
                                 schema='MicrolocationSchema',
                                 type_='microlocation')
    track = Relationship(attribute='track',
                         self_view='v1.session_track',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.track_detail',
                         related_view_kwargs={'session_id': '<id>'},
                         schema='TrackSchema',
                         type_='track')
    session_type = Relationship(attribute='session_type',
                                self_view='v1.session_session_type',
                                self_view_kwargs={'id': '<id>'},
                                related_view='v1.session_type_detail',
                                related_view_kwargs={'session_id': '<id>'},
                                schema='SessionTypeSchema',
                                type_='session-type')
    event = Relationship(attribute='event',
                         self_view='v1.session_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'session_id': '<id>'},
                         schema='EventSchema',
                         type_='event')
    speakers = Relationship(
        attribute='speakers',
        self_view='v1.session_speaker',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.speaker_list',
        related_view_kwargs={'session_id': '<id>'},
        schema='SpeakerSchema',
        type_='speaker')


class SessionList(ResourceList):
    """
    List and create Sessions
    """

    def query(self, view_kwargs):
        query_ = self.session.query(Session)
        if view_kwargs.get('track_id') is not None:
            track = safe_query(self, Track, 'id', view_kwargs['track_id'], 'track_id')
            query_ = query_.join(Track).filter(Track.id == track.id)
        if view_kwargs.get('session_type_id') is not None:
            session_type = safe_query(self, SessionType, 'id', view_kwargs['session_type_id'], 'session_type_id')
            query_ = query_.join(SessionType).filter(SessionType.id == session_type.id)
        if view_kwargs.get('microlocation_id') is not None:
            microlocation = safe_query(self, Microlocation, 'id', view_kwargs['microlocation_id'], 'microlocation_id')
            query_ = query_.join(Microlocation).filter(Microlocation.id == microlocation.id)
        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
            query_ = query_.join(Event).filter(Event.id == event.id)
        elif view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
            query_ = query_.join(Event).filter(Event.identifier == event.id)
        if view_kwargs.get('speaker_id'):
            query_ = Session.query.filter(Session.speakers.any(id=view_kwargs['speaker_id']))
        return query_

    def before_create_object(self, data, view_kwargs):
        # Permission Manager ensures there is event ID if any event_identifier provided
        event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
        data['event_id'] = event.id

    view_kwargs = True
    decorators = (api.has_permission('is_coorganizer', fetch="event_id",
                  fetch_as="event_id", methods="POST",
                  check=lambda a: a.get('event_id') or a.get('event_identifier')), )
    schema = SessionSchema
    data_layer = {'session': db.session,
                  'model': Session,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object
                  }}


class SessionDetail(ResourceDetail):
    """
    Session detail by id
    """
    def before_get_object(self, view_kwargs):
        if view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'identifier')
            view_kwargs['event_id'] = event.id

    decorators = (api.has_permission('is_coorganizer', fetch="event_id",
                                     fetch_as="event_id", model=Session, methods="PATCH,DELETE"),)
    schema = SessionSchema
    data_layer = {'session': db.session,
                  'model': Session,
                  'methods': {'before_get_object': before_get_object}}


class SessionRelationship(ResourceRelationship):
    """
    Session Relationship
    """
    schema = SessionSchema
    data_layer = {'session': db.session,
                  'model': Session}
