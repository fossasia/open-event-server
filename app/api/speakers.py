from flask_rest_jsonapi.exceptions import ObjectNotFound
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema, Relationship
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from sqlalchemy.orm.exc import NoResultFound

from app.api.helpers.utilities import dasherize
from app.api.helpers.permissions import jwt_required, is_coorganizer
from app.models import db
from app.models.speaker import Speaker
from app.models.session import Session
from app.models.user import User
from app.models.event import Event


class SpeakerSchema(Schema):
    class Meta:
        type_ = 'speaker'
        self_view = 'v1.speaker_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Str(required=True)
    photo_url = fields.Str()
    thumbnail_image_url = fields.Str()
    small_image_url = fields.Str()
    icon_image_url = fields.Str()
    short_biography = fields.Str()
    long_biography = fields.Str()
    speaking_experience = fields.Str()
    mobile = fields.Str()
    website = fields.Url()
    twitter = fields.Url()
    facebook = fields.Url()
    github = fields.Url()
    linkedin = fields.Url()
    organisation = fields.Str()
    is_featured = fields.Boolean(default=False)
    position = fields.Str()
    country = fields.Str()
    city = fields.Str()
    gender = fields.Str()
    heard_from = fields.Str()
    sponsorship_required = fields.Str()
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
    def query(self, view_kwargs):
        query_ = self.session.query(Speaker)
        if view_kwargs.get('event_id'):
            query_ = query_.join(Event).filter(Event.id == view_kwargs['event_id'])
        return query_

    def before_create_object(self, data, view_kwargs):
        if view_kwargs.get('event_id'):
            event = self.session.query(Event).filter_by(id=view_kwargs['event_id']).one()
            data['event_id'] = event.id
        elif view_kwargs.get('identifier'):
            event = self.session.query(Event).filter_by(identifier=view_kwargs['identifier']).one()
            data['event_id'] = event.id

    view_kwargs = True
    decorators = (jwt_required,)
    schema = SpeakerSchema
    data_layer = {'session': db.session,
                  'model': Speaker,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object
                  }}


class SpeakerDetail(ResourceDetail):
    def before_get_object(self, view_kwargs):
        if view_kwargs.get('session_id'):
            try:
                sessions = self.session.query(Session).filter_by(id=view_kwargs['session_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'session_id'},
                                     "Session: {} not found".format(view_kwargs['session_id']))
            else:
                if sessions.id:
                    view_kwargs['id'] = sessions.id
                else:
                    view_kwargs['id'] = None

        if view_kwargs.get('user_id'):
            try:
                user = self.session.query(User).filter_by(id=view_kwargs['user_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'user_id'},
                                     "User: {} not found".format(view_kwargs['user_id']))
            else:
                if user.id:
                    view_kwargs['id'] = user.id
                else:
                    view_kwargs['id'] = None

    decorators = (jwt_required,)
    schema = SpeakerSchema
    data_layer = {'session': db.session,
                  'model': Speaker,
                  'methods': {'before_get_object': before_get_object}}


class SpeakerRelationship(ResourceRelationship):
    decorators = (jwt_required,)
    schema = SpeakerSchema
    data_layer = {'session': db.session,
                  'model': Speaker}
