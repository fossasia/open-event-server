from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from marshmallow import validates_schema
import marshmallow.validate as validate
from sqlalchemy.orm.exc import NoResultFound
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.bootstrap import api
from app.api.events import Event
from app.api.helpers.utilities import dasherize
from app.api.helpers.permissions import jwt_required
from app.models import db
from app.models.session import Session
from app.models.speaker import Speaker
from app.models.track import Track
from app.models.session_type import SessionType
from app.models.microlocation import Microlocation
from app.api.helpers.exceptions import UnprocessableEntity


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

    @validates_schema
    def validate_date(self, data):
        if data['starts_at'] >= data['ends_at']:
            raise UnprocessableEntity({'pointer': '/data/attributes/ends-at'}, "ends-at should be after starts-at")

    id = fields.Str(dump_only=True)
    title = fields.Str(required=True)
    subtitle = fields.Str()
    event_url = fields.Url()
    level = fields.Int()
    short_abstract = fields.Str()
    long_abstract = fields.Str()
    comments = fields.Str()
    starts_at = fields.DateTime(required=True)
    ends_at = fields.DateTime(required=True)
    language = fields.Str()
    slides_url = fields.Url(attribute='slides')
    videos_url = fields.Url(attribute='videos')
    audios_url = fields.Url(attribute='audios')
    signup_url = fields.Url()
    state = fields.Str(validate=validate.OneOf(choices=["pending", "accepted", "confirmed", "rejected", "draft"]))
    created_at = fields.DateTime(dump_only=True)
    deleted_at = fields.DateTime(dump_only=True)
    submitted_at = fields.DateTime()
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
    speaker = Relationship(attribute='speakers',
                           self_view='v1.session_speaker',
                           self_view_kwargs={'id': '<id>'},
                           related_view='v1.speaker_detail',
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
            query_ = query_.join(Track).filter(Track.id == view_kwargs['track_id'])
        if view_kwargs.get('session_type_id') is not None:
            query_ = query_.join(SessionType).filter(
                SessionType.id == view_kwargs['session_type_id'])
        if view_kwargs.get('microlocation_id') is not None:
            query_ = query_.join(Microlocation).filter(
                Microlocation.id == view_kwargs['microlocation_id'])
        if view_kwargs.get('event_id'):
            query_ = query_.join(Event).filter(Event.id == view_kwargs['event_id'])
        elif view_kwargs.get('event_identifier'):
            query_ = query_.join(Event).filter(Event.identifier == view_kwargs['event_identifier'])
        if view_kwargs.get('speaker_id') is not None:
            query_ = query_.join(Speaker).filter(
                Speaker.id == view_kwargs['speaker_id'])
        if view_kwargs.get('speaker_id'):
            query_ = Speaker.query.filter(Speaker.sessions.any(
                id=view_kwargs['speaker_id']))
        return query_

    def before_create_object(self, data, view_kwargs):
        if view_kwargs.get('event_id') is not None:
            try:
                event = self.session.query(Event).filter_by(id=view_kwargs['event_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'event_id'},
                                     "Event: {} not found".format(view_kwargs['event_id']))
            else:
                data['event_id'] = event.id

        if view_kwargs.get('speaker_id'):
            speaker = Speaker.query.filter(Speaker.sessions.any(
                id=view_kwargs['speaker_id'])).one()
            data['speaker_id'] = speaker.id

    view_kwargs = True
    decorators = (api.has_permission('is_coorganizer', fetch="event_id",
                                     fetch_as="event_id", methods="POST",
                                     check=lambda a: a.get('event_id') or a.get('event_identifier')),)
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

    def before_get_object(self, data, view_kwargs):
        if view_kwargs.get('event_identifier'):
            try:
                event = self.session.query(Event).filter_by(identifier=view_kwargs['event_identifier']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'event_identifier'},
                                     "Event: {} not found".format(view_kwargs['event_identifier']))
            else:
                view_kwargs['event_id'] = event.id

        if view_kwargs.get('speaker_id'):
            print("in resource detail")
            speaker = Speaker.query.filter(Speaker.sessions.any(
                id=view_kwargs['speaker_id'])).one()
            data['speaker_id'] = speaker.id

    decorators = (api.has_permission('is_coorganizer', fetch="event_id",
                                     fetch_as="event_id",
                                     model=Session,
                                     methods="PATCH,DELETE"),)
    schema = SessionSchema
    data_layer = {'session': db.session,
                  'model': Session,
                  'methods': {
                      'before_get_object': before_get_object}}


class SessionRelationship(ResourceRelationship):
    """
    Session Relationship
    """
    decorators = (jwt_required,)
    schema = SessionSchema
    data_layer = {'session': db.session,
                  'model': Session}
