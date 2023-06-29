from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

from app.api.helpers.utilities import dasherize
from utils.common import use_defaults


@use_defaults()
class CustomFormTranslateSchema(Schema):
    """API Schema for Custom Forms database model"""

    class Meta:
        """Meta class for CustomForm Schema"""

        type_ = 'custom-form-translate'
        self_view = 'v1.custom_form_translate_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Integer(dump_only=True)
    name = fields.Str(required=True)
    custom_form = Relationship(
        self_view='v1.custom_form_translate_form',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.custom_form_detail',
        related_view_kwargs={'custom_form_translate_id': '<id>'},
        schema='CustomFormSchema',
        type_='custom_form',
    )
    language_code = fields.Str(required=True)
    form_id = fields.Str(required=True)
