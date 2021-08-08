from datetime import datetime

from flask_rest_jsonapi.exceptions import ObjectNotFound
from marshmallow import Schema, validate, validates_schema
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship
from sqlalchemy.orm.exc import NoResultFound

from app.api.helpers.errors import UnprocessableEntityError
from app.api.helpers.fields import CustomFormValueField
from app.api.helpers.permission_manager import has_access
from app.api.helpers.static import LEVEL_CHOICES
from app.api.helpers.utilities import dasherize
from app.api.helpers.validations import validate_complex_fields_json
from app.api.schema.base import SoftDeletionSchema
from app.models.helpers.versioning import clean_html
from app.models.session import Session
from utils.common import use_defaults


class DocumentLinkSchema(Schema):
    name = fields.String(required=True)
    link = fields.String(required=True)


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
    def validate_fields(self, data, original_data):
        is_patch_request = 'id' in original_data['data']
        if is_patch_request:
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

        if data.get('starts_at') and data.get('ends_at'):
            if data['starts_at'] >= data['ends_at']:
                raise UnprocessableEntityError(
                    {'pointer': '/data/attributes/ends-at'},
                    "ends-at should be after starts-at",
                )
            if not is_patch_request and datetime.timestamp(
                data['starts_at']
            ) <= datetime.timestamp(datetime.now()):
                raise UnprocessableEntityError(
                    {'pointer': '/data/attributes/starts-at'},
                    "starts-at should be after current date-time",
                )

        if 'microlocation' in data:
            if not has_access('is_coorganizer', event_id=data['event']):
                del data['microlocation']

        validate_complex_fields_json(self, data, original_data)

    id = fields.Str(dump_only=True)
    title = fields.Str(required=True)
    subtitle = fields.Str(allow_none=True)
    level = fields.Str(allow_none=True, validate=validate.OneOf(choices=LEVEL_CHOICES))
    short_abstract = fields.Str(allow_none=True)
    long_abstract = fields.Str(allow_none=True)
    comments = fields.Str(allow_none=True)
    starts_at = fields.DateTime(allow_none=True)
    ends_at = fields.DateTime(allow_none=True)
    language = fields.Str(allow_none=True)
    slides_url = fields.Url(allow_none=True)
    slides = fields.Nested(DocumentLinkSchema, many=True, allow_none=True)
    website = fields.Url(allow_none=True)
    twitter = fields.Url(allow_none=True)
    facebook = fields.Url(allow_none=True)
    github = fields.Url(allow_none=True)
    linkedin = fields.Url(allow_none=True)
    instagram = fields.Url(allow_none=True)
    gitlab = fields.Url(allow_none=True)
    mastodon = fields.Url(allow_none=True)
    video_url = fields.Url(allow_none=True)
    audio_url = fields.Url(allow_none=True)
    signup_url = fields.Url(allow_none=True)
    state = fields.Str(
        validate=validate.OneOf(
            choices=[
                "pending",
                "accepted",
                "confirmed",
                "rejected",
                "draft",
                "canceled",
                "withdrawn",
            ]
        ),
        allow_none=True,
        missing='draft',
    )
    created_at = fields.DateTime(dump_only=True)
    deleted_at = fields.DateTime(dump_only=True)
    submitted_at = fields.DateTime(allow_none=True)
    is_mail_sent = fields.Boolean()
    is_locked = fields.Boolean(default=False)
    last_modified_at = fields.DateTime(dump_only=True)
    send_email = fields.Boolean(load_only=True, allow_none=True)
    average_rating = fields.Float(dump_only=True)
    rating_count = fields.Integer(dump_only=True)
    favourite_count = fields.Integer(dump_only=True)
    complex_field_values = CustomFormValueField(allow_none=True)
    microlocation = Relationship(
        self_view='v1.session_microlocation',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.microlocation_detail',
        related_view_kwargs={'session_id': '<id>'},
        schema='MicrolocationSchema',
        type_='microlocation',
    )
    track = Relationship(
        self_view='v1.session_track',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.track_detail',
        related_view_kwargs={'session_id': '<id>'},
        schema='TrackSchema',
        type_='track',
    )
    session_type = Relationship(
        self_view='v1.session_session_type',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.session_type_detail',
        related_view_kwargs={'session_id': '<id>'},
        schema='SessionTypeSchema',
        type_='session-type',
    )
    event = Relationship(
        self_view='v1.session_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_detail',
        related_view_kwargs={'session_id': '<id>'},
        schema='EventSchemaPublic',
        type_='event',
    )
    feedbacks = Relationship(
        self_view='v1.session_feedbacks',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.feedback_list',
        related_view_kwargs={'session_id': '<id>'},
        schema='FeedbackSchema',
        many=True,
        type_='feedback',
    )
    speakers = Relationship(
        many=True,
        self_view='v1.session_speaker',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.speaker_list',
        related_view_kwargs={'session_id': '<id>'},
        schema='SpeakerSchema',
        type_='speaker',
    )
    exhibitors = Relationship(
        dump_only=True,
        many=True,
        self_view='v1.session_exhibitor',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.exhibitor_list',
        related_view_kwargs={'session_id': '<id>'},
        schema='ExhibitorSchema',
        type_='exhibitor',
    )
    creator = Relationship(
        attribute='user',
        self_view='v1.session_user',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_detail',
        related_view_kwargs={'session_id': '<id>'},
        schema='UserSchemaPublic',
        type_='user',
    )
    favourite = Relationship(
        dump_only=True,
        self_view='v1.session_user_favourite_sessions',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_favourite_sessions_list',
        related_view_kwargs={'session_id': '<id>'},
        schema='UserFavouriteSessionSchema',
        type_='user-favourite-session',
    )
    favourites = Relationship(
        self_view='v1.session_user_favourite_sessions',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_favourite_sessions_list',
        related_view_kwargs={'session_id': '<id>'},
        schema='UserFavouriteSessionSchema',
        many=True,
        type_='user-favourite-session',
    )
    speaker_invites = Relationship(
        self_view='v1.session_speaker_invites',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.speaker_invite_list',
        related_view_kwargs={'session_id': '<id>'},
        schema='SpeakerInviteSchema',
        many=True,
        type_='speaker-invite',
    )


# Used for customization of email notification subject and message body
class SessionNotifySchema(Schema):
    subject = fields.Str(required=False, validate=validate.Length(max=250))
    message = fields.Str(required=False, validate=validate.Length(max=5000))
    bcc = fields.List(fields.String(), default=[])

    @validates_schema
    def validate_fields(self, data):
        if not data:
            return
        data['message'] = clean_html(data.get('message'), allow_link=True)
