from marshmallow import Schema, validate
from marshmallow.schema import Schema as JsonSchema
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship
from marshmallow_jsonapi.flask import Schema as JSONAPISchema

from app.api.helpers.utilities import dasherize
from app.api.schema.base import TrimmedEmail
from app.models.exhibitor import Exhibitor


class ExhibitorSocialLinkSchema(Schema):
    name = fields.String(required=True)
    link = fields.String(required=True)
    is_custom = fields.Boolean(default=False)


class ExhibitorSchema(JSONAPISchema):
    class Meta:

        type_ = 'exhibitor'
        self_view = 'v1.exhibitor_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    status = fields.Str(
        allow_none=True,
        default=Exhibitor.Status.PENDING,
        validate=validate.OneOf(choices=Exhibitor.Status.STATUSES),
    )
    description = fields.Str(allow_none=True)
    url = fields.Url(allow_none=True)
    position = fields.Integer(allow_none=True, default=0)
    logo_url = fields.Url(allow_none=True)
    banner_url = fields.Url(allow_none=True)
    thumbnail_image_url = fields.Url(allow_none=True)
    enable_video_room = fields.Boolean(allow_none=True, default=False)
    video_url = fields.Url(allow_none=True)
    slides_url = fields.Url(allow_none=True)
    contact_email = TrimmedEmail(allow_none=True)
    contact_link = fields.Str(allow_none=True)
    social_links = fields.Nested(ExhibitorSocialLinkSchema, many=True, allow_none=True)
    event = Relationship(
        self_view='v1.exhibitor_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_detail',
        related_view_kwargs={'exhibitor_id': '<id>'},
        schema='EventSchemaPublic',
        type_='event',
    )
    sessions = Relationship(
        many=True,
        self_view='v1.exhibitor_session',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.session_list',
        related_view_kwargs={'exhibitor_id': '<id>'},
        schema='SessionSchema',
        type_='session',
    )


class ExhibitorReorderSchema(JsonSchema):
    exhibitor = fields.Integer(required=True)
    position = fields.Integer(required=True)
