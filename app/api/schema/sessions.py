from flask_rest_jsonapi.exceptions import ObjectNotFound
from marshmallow import validates_schema, validate
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime

from app.api.helpers.exceptions import UnprocessableEntity, ForbiddenException
from app.api.helpers.permission_manager import has_access
from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema
from app.models.session import Session
from utils.common import use_defaults


@use_defaults()
class SessionSchema(SoftDeletionSchema):
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
            try:
                session = Session.query.filter_by(id=original_data['data']['id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': '{id}'}, "Session: not found")

            if 'starts_at' not in data:
                data['starts_at'] = session.starts_at

            if 'ends_at' not in data:
                data['ends_at'] = session.ends_at

            if 'event' not in data:
                data['event'] = session.event_id

        if data['starts_at'] and data['ends_at']:
            if data['starts_at'] >= data['ends_at']:
                raise UnprocessableEntity(
                    {'pointer': '/data/attributes/ends-at'}, "ends-at should be after starts-at")
            if datetime.timestamp(data['starts_at']) <= datetime.timestamp(datetime.now()):
                raise UnprocessableEntity(
                    {'pointer': '/data/attributes/starts-at'}, "starts-at should be after current date-time")

        if 'state' in data:
            if data['state'] is not 'draft' or not 'pending':
                if not has_access('is_coorganizer', event_id=data['event']):
                    return ForbiddenException({'source': ''}, 'Co-organizer access is required.')

        if 'track' in data:
            if not has_access('is_coorganizer', event_id=data['event']):
                return ForbiddenException({'source': ''}, 'Co-organizer access is required.')

        if 'microlocation' in data:
            if not has_access('is_coorganizer', event_id=data['event']):
                return ForbiddenException({'source': ''}, 'Co-organizer access is required.')

    id = fields.Str(dump_only=True)
    title = fields.Str(required=True)
    subtitle = fields.Str(allow_none=True)
    level = fields.Str(allow_none=True)
    short_abstract = fields.Str(allow_none=True)
    long_abstract = fields.Str(allow_none=True)
    comments = fields.Str(allow_none=True)
    starts_at = fields.DateTime(allow_none=True)
    ends_at = fields.DateTime(allow_none=True)
    language = fields.Str(allow_none=True)
    slides_url = fields.Url(allow_none=True)
    video_url = fields.Url(allow_none=True)
    audio_url = fields.Url(allow_none=True)
    signup_url = fields.Url(allow_none=True)
    state = fields.Str(validate=validate.OneOf(choices=["pending", "accepted", "confirmed", "rejected", "draft"]),
                       allow_none=True, default='draft')
    created_at = fields.DateTime(dump_only=True)
    deleted_at = fields.DateTime(dump_only=True)
    submitted_at = fields.DateTime(allow_none=True)
    is_mail_sent = fields.Boolean()
    last_modified_at = fields.DateTime(dump_only=True)
    send_email = fields.Boolean(load_only=True, allow_none=True)
    average_rating = fields.Float(dump_only=True)
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
                         schema='EventSchemaPublic',
                         type_='event')
    feedbacks = Relationship(attribute='feedbacks',
                             self_view='v1.session_feedbacks',
                             self_view_kwargs={'id': '<id>'},
                             related_view='v1.feedback_list',
                             related_view_kwargs={'session_id': '<id>'},
                             schema='FeedbackSchema',
                             many=True,
                             type_='feedback')
    speakers = Relationship(attribute='speakers',
                            many=True,
                            self_view='v1.session_speaker',
                            self_view_kwargs={'id': '<id>'},
                            related_view='v1.speaker_list',
                            related_view_kwargs={'session_id': '<id>'},
                            schema='SpeakerSchema',
                            type_='speaker')
    creator = Relationship(attribute='user',
                           self_view='v1.session_user',
                           self_view_kwargs={'id': '<id>'},
                           related_view='v1.user_detail',
                           related_view_kwargs={'session_id': '<id>'},
                           schema='UserSchemaPublic',
                           type_='user')
