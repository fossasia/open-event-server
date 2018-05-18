from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from app.api.helpers.utilities import dasherize
from utils.common import use_defaults


@use_defaults()
class ModuleSchema(Schema):
    """
    Admin Api schema for modules Model
    """
    class Meta:
        """
        Meta class for module Api Schema
        """
        type_ = 'module'
        self_view = 'v1.module_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    ticket_include = fields.Boolean(default=False)
    payment_include = fields.Boolean(default=False)
    donation_include = fields.Boolean(default=False)
