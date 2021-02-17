from marshmallow import validate
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

from app.api.helpers.utilities import dasherize
from utils.common import use_defaults


@use_defaults()
class CustomFormSchema(Schema):
    """
    API Schema for Custom Forms database model
    """

    class Meta:
        """
        Meta class for CustomForm Schema
        """

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
            ]
        ),
    )
    name = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    is_required = fields.Boolean(default=False)
    is_included = fields.Boolean(default=False)
    is_public = fields.Boolean(default=False)
    position = fields.Integer(allow_none=True, default=0)
    is_complex = fields.Boolean(dump_only=True)
    is_fixed = fields.Boolean(default=False)
    event = Relationship(
        self_view='v1.custom_form_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_detail',
        related_view_kwargs={'custom_form_id': '<id>'},
        schema='EventSchemaPublic',
        type_='event',
    )
