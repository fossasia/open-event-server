from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from app.api.helpers.utilities import dasherize


class ActivitySchema(Schema):
    """
    Api schema for Activity Model
    """

    class Meta:
        """
        Meta class for Activity Api Schema
        """

        type_ = 'activity'
        self_view = 'v1.activity_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    actor = fields.Str(allow_none=True)
    time = fields.DateTime(allow_none=True)
    action = fields.Str(allow_none=True)
