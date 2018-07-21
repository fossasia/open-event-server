from marshmallow import validate as validate
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema
from utils.common import use_defaults


@use_defaults()
class CustomFormSchema(SoftDeletionSchema):
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
    form = fields.Str(required=True)
    type = fields.Str(default="text", validate=validate.OneOf(
        choices=["text", "checkbox", "select", "file", "image", "email",
                 "number"]))
    is_required = fields.Boolean(default=False)
    is_included = fields.Boolean(default=False)
    is_fixed = fields.Boolean(default=False)
    event = Relationship(attribute='event',
                         self_view='v1.custom_form_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'custom_form_id': '<id>'},
                         schema='EventSchemaPublic',
                         type_='event')
