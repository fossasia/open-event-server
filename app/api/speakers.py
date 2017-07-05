from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema, Relationship
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.helpers.utilities import dasherize
from app.api.helpers.permissions import jwt_required, current_identity
from app.models import db
from app.models.speaker import Speaker
from app.models.session import Session
from app.models.user import User
from app.models.event import Event
from app.api.helpers.db import safe_query


class SpeakerSchema(Schema):
    """
    Speaker Schema based on Speaker Model
    """
    class Meta:
        """
        Meta class for speaker schema
        """
        type_ = 'speaker'
        self_view = 'v1.speaker_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Str(required=True)
    photo_url = fields.Url(allow_none=True)
    thumbnail_image_url = fields.Url(allow_none=True)
    small_image_url = fields.Url(allow_none=True)
    icon_image_url = fields.Url(allow_none=True)
    short_biography = fields.Str(allow_none=True)
    long_biography = fields.Str(allow_none=True)
    speaking_experience = fields.Str(allow_none=True)
    mobile = fields.Str(allow_none=True)
    website = fields.Url(allow_none=True)
    twitter = fields.Url(allow_none=True)
    facebook = fields.Url(allow_none=True)
    github = fields.Url(allow_none=True)
    linkedin = fields.Url(allow_none=True)
    organisation = fields.Str(allow_none=True)
    is_featured = fields.Boolean(default=False)
    position = fields.Str(allow_none=True)
    country = fields.Str(allow_none=True)
    city = fields.Str(allow_none=True)
    gender = fields.Str(allow_none=True)
    heard_from = fields.Str(allow_none=True)
    sponsorship_required = fields.Str(allow_none=True)
    event = Relationship(attribute='event',
                         self_view='v1.speaker_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'speaker_id': '<id>'},
                         schema='EventSchema',
                         type_='event')
    user = Relationship(attribute='user',
                        self_view='v1.speaker_user',
                        self_view_kwargs={'id': '<id>'},
                        related_view='v1.user_detail',
                        related_view_kwargs={'speaker_id': '<id>'},
                        schema='UserSchema',
                        type_='user')
    sessions = Relationship(attribute='sessions',
                            self_view='v1.speaker_session',
                            self_view_kwargs={'id': '<id>'},
                            related_view='v1.session_list',
                            related_view_kwargs={'speaker_id': '<id>'},
                            schema='SessionSchema',
                            type_='session')


class SpeakerList(ResourceList):
    """
    List and create speakers
    """
    def query(self, view_kwargs):
        """
        query method for speakers list class
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(Speaker)
        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
            query_ = query_.join(Event).filter(Event.id == event.id)
        elif view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
            query_ = query_.join(Event).filter(Event.id == event.id)
        if view_kwargs.get('user_id'):
            user = safe_query(self, User, 'id', view_kwargs['user_id'], 'user_id')
            query_ = query_.join(User).filter(User.id == user.id)
        if view_kwargs.get('session_id'):
            session = safe_query(self, Session, 'id', view_kwargs['session_id'], 'session_id')
            # session-speaker :: many-to-many relationship
            query_ = Speaker.query.filter(Speaker.sessions.any(id=session.id))
        return query_

    def before_post(self, args, kwargs, data):
        """
        method to add user_id to view_kwargs before post
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        kwargs['user_id'] = current_identity.id

    def before_create_object(self, data, view_kwargs):
        """
        before create object method for speaker list class
        :param data:
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
            data['event_id'] = event.id
        elif view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
            data['event_id'] = event.id
        data['user_id'] = current_identity.id

    view_kwargs = True
    decorators = (jwt_required,)
    schema = SpeakerSchema
    data_layer = {'session': db.session,
                  'model': Speaker,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object,
                      'before_post': before_post
                  }}


class SpeakerDetail(ResourceDetail):
    """
    Speakers Detail by id
    """
    decorators = (jwt_required,)
    schema = SpeakerSchema
    data_layer = {'session': db.session,
                  'model': Speaker}


class SpeakerRelationship(ResourceRelationship):
    """
    Speaker Relationship class
    """
    decorators = (jwt_required,)
    schema = SpeakerSchema
    data_layer = {'session': db.session,
                  'model': Speaker}
