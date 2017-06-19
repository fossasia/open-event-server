from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from marshmallow import validates_schema
import marshmallow.validate as validate

from app.api.events import Event
from app.api.helpers.utilities import dasherize
from app.api.helpers.permissions import jwt_required
from app.models import db
from app.models.session import Session
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
        if view_kwargs.get('id'):
            query_ = query_.join(Event).filter(Event.id == view_kwargs['id'])
        elif view_kwargs.get('identifier'):
            query_ = query_.join(Event).filter(Event.identifier == view_kwargs['identifier'])
        return query_

    def before_create_object(self, data, view_kwargs):
        if view_kwargs.get('track_id') is not None:
            track = self.session.query(Track).filter_by(id=view_kwargs['track_id']).one()
            data['track_id'] = track.id
        if view_kwargs.get('session_type_id') is not None:
            session_type = self.session.query(SessionType).filter_by(
                id=view_kwargs['session_type_id']).one()
            data['session_type_id'] = session_type.id
        if view_kwargs.get('microlocation_id') is not None:
            microlocation = self.session.query(Microlocation).filter_by(
                id=view_kwargs['microlocation_id']).one()
            data['microlocation_id'] = microlocation.id

    view_kwargs = True
    decorators = (jwt_required, )
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
    decorators = (jwt_required, )
    schema = SessionSchema
    data_layer = {'session': db.session,
                  'model': Session}


class SessionRelationship(ResourceRelationship):
    """
    Session Relationship
    """
    decorators = (jwt_required, )
    schema = SessionSchema
    data_layer = {'session': db.session,
                  'model': Session}
