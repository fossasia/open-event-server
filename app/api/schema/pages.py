from marshmallow import validate as validate
from marshmallow_jsonapi import fields

from app.api.helpers.utilities import dasherize
from app.api.schema.base import BaseSchema
from utils.common import use_defaults


@use_defaults()
class PageSchema(BaseSchema):
    """
    Api schema for page Model
    """
    class Meta:
        """
        Meta class for page Api Schema
        """
        type_ = 'page'
        self_view = 'v1.page_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    title = fields.Str(allow_none=True)
    url = fields.String(required=True)
    description = fields.Str(allow_none=True)
    place = fields.Str(validate=validate.OneOf(choices=["footer", "event"]), allow_none=True)
    language = fields.Str(allow_none=True)
    index = fields.Integer(default=0)
