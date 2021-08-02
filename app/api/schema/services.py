from marshmallow import validate
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from app.api.helpers.utilities import dasherize
from utils.common import use_defaults


@use_defaults()
class ServiceSchema(Schema):
    """
    API Schema for Service Model
    """

    class Meta:
        """
        Meta class for Service API schema
        """

        type_ = 'service'
        self_view = 'v1.service_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'v1.service_list'
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(
        default="track",
        validate=validate.OneOf(
            choices=["microlocation", "session", "speaker", "track", "sponsor"]
        ),
    )
