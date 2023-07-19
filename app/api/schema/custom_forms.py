from marshmallow import validate
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

from app.api.custom.schema.custom_form_translate import TranslationSchema
from app.api.helpers.utilities import dasherize
from utils.common import use_defaults


@use_defaults()
class CustomFormSchema(Schema):
    """API Schema for Custom Form Translates database model"""

    class Meta:
        """Meta class for Custom Form Translates Schema"""

        type_ = 'custom-form'
        self_view = 'v1.custom_form_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Integer(dump_only=True)
    field_identifier = fields.Str(required=True)
    form = fields.Str(
        required=True,
        validate=validate.OneOf(choices=["attendee", "session", "speaker"]),
    )
    type = fields.Str(
        default="text",
        validate=validate.OneOf(
            choices=[
                "text",
                "checkbox",
                "select",
                "file",
                "image",
                "email",
                "number",
                "paragraph",
                "richtextlink",
                "boolean",
                "year",
            ]
        ),
    )
    name = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    is_required = fields.Boolean(default=False)
    is_included = fields.Boolean(default=False)
    is_public = fields.Boolean(default=False)
    position = fields.Integer(allow_none=True, default=0)
    is_complex = fields.Boolean(dump_only=True, default=False)
    is_fixed = fields.Boolean(default=False)
    event = Relationship(
        self_view='v1.custom_form_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_detail',
        related_view_kwargs={'custom_form_id': '<id>'},
        schema='EventSchemaPublic',
        type_='event',
    )
    form_id = fields.Str(allow_none=True)
    min = fields.Integer(allow_none=True, default=0)
    max = fields.Integer(allow_none=True, default=10)
    main_language = fields.Str(allow_none=True)
    is_allow_edit = fields.Boolean(default=False)
    translations = fields.Nested(TranslationSchema, many=True)
