from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema
from utils.common import use_defaults


@use_defaults()
class CustomFormOptionSchema(SoftDeletionSchema):
    """
    API Schema for Custom Forms database model
    """

    class Meta:
        """
        Meta class for CustomForm Schema
        """

        type_ = 'custom-form-option'
        self_view = 'v1.custom_form_option_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Integer(dump_only=True)
    value = fields.Str(required=True)
    custom_form = Relationship(
        self_view='v1.custom_form_option_form',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.custom_form_detail',
        related_view_kwargs={'custom_form_option_id': '<id>'},
        schema='CustomFormSchema',
        type_='custom_form',
    )
