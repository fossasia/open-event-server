from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema, Relationship
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound
from flask import request

from app.api.helpers.utilities import dasherize
from app.api.helpers.permissions import jwt_required
from app.models import db
from app.models.speaker import Speaker
from app.models.session import Session
from app.models.user import User
from app.models.event import Event
from app.api.helpers.db import safe_query
from app.api.bootstrap import api
from app.api.helpers.utilities import require_relationship
from app.api.helpers.permission_manager import has_access


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
                            many=True,
                            type_='session')


class SpeakerListPost(ResourceList):
    """
    List and create speakers
    """

    def before_post(self, args, kwargs, data):
        """
        method to add user_id to view_kwargs before post
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['event', 'user'], data)

        if not has_access('is_coorganizer', event_id=data['event']):
                event = safe_query(self, Event, 'id', data['event'], 'event_id')
                if event.state == "draft":
                    raise ObjectNotFound({'parameter': 'event_id'},
                                         "Event: {} not found".format(data['event_id']))

        if 'sessions' in data:
            session_ids = data['sessions']
            for session_id in session_ids:
                if not has_access('is_session_self_submitted', session_id=session_id):
                    raise ObjectNotFound({'parameter': 'session_id'},
                                         "Session: {} not found".format(session_id))

    schema = SpeakerSchema
    methods = ['POST', ]
    data_layer = {'session': db.session,
                  'model': Speaker
                  }


class SpeakerList(ResourceList):
    """
    List speakers based on different params from view_kwargs
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
            if event.state != 'published':
                if 'Authorization' in request.headers and has_access('is_coorganizer', event_id=event.id):
                    query_ = query_.join(Event).filter(Event.id == event.id)
                else:
                    raise ObjectNotFound({'parameter': 'event_id'},
                                         "Event: {} not found".format(view_kwargs['event_identifier']))
            else:
                query_ = query_.join(Event).filter(Event.id == event.id)
        elif view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
            if event.state != 'published':
                if 'Authorization' in request.headers and has_access('is_coorganizer', event_id=event.id):
                    query_ = query_.join(Event).filter(Event.id == event.id)
                else:
                    raise ObjectNotFound({'parameter': 'event_identifier'},
                                         "Event: {} not found".format(view_kwargs['event_identifier']))
            else:
                query_ = query_.join(Event).filter(Event.id == event.id)

        if view_kwargs.get('user_id'):
            user = safe_query(self, User, 'id', view_kwargs['user_id'], 'user_id')
            query_ = query_.join(User).filter(User.id == user.id)

        if view_kwargs.get('session_id'):
            session = safe_query(self, Session, 'id', view_kwargs['session_id'], 'session_id')
            # session-speaker :: many-to-many relationship
            query_ = Speaker.query.filter(Speaker.sessions.any(id=session.id))
            if 'Authorization' in request.headers and not has_access('is_coorganizer', event_id=session.event_id):
                if not has_access('is_session_self_submitted', session_id=session.id):
                    query_ = query_.filter(Session.state == "approved" or Session.state == "accepted")

        return query_

    view_kwargs = True
    schema = SpeakerSchema
    methods = ['GET', ]
    data_layer = {'session': db.session,
                  'model': Speaker,
                  'methods': {
                      'query': query,
                  }}


class SpeakerDetail(ResourceDetail):
    """
    Speakers Detail by id
    """
    decorators = (api.has_permission('is_coorganizer_or_user_itself', methods="PATCH,DELETE", fetch="event_id",
                                     fetch_as="event_id", model=Speaker, check=lambda a: a.get('id') is not None),)
    schema = SpeakerSchema
    data_layer = {'session': db.session,
                  'model': Speaker}


class SpeakerRelationshipRequired(ResourceRelationship):
    """
    Speaker Relationship class for required entities
    """
    decorators = (api.has_permission('is_coorganizer_or_user_itself', methods="PATCH,DELETE", fetch="event_id",
                                     fetch_as="event_id", model=Speaker),)
    methods = ['GET', 'PATCH']
    schema = SpeakerSchema
    data_layer = {'session': db.session,
                  'model': Speaker}


class SpeakerRelationshipOptional(ResourceRelationship):
    """
    Speaker Relationship class
    """
    decorators = (api.has_permission('is_coorganizer_or_user_itself', methods="PATCH,DELETE", fetch="event_id",
                                     fetch_as="event_id", model=Speaker),)
    schema = SpeakerSchema
    data_layer = {'session': db.session,
                  'model': Speaker}
