from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema
from app.models.api_key import ApiKey
from utils.common import use_defaults


@use_defaults()
class ApiKeySchema(SoftDeletionSchema):
    """
    Api schema for ApiKey model
    """

    class Meta:
        """
        Meta class for ApiKey schema
        """

        type_ = 'api-key'
        self_view = 'v1.api_key_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Integer(dump_only=True)
    name = fields.Str(allow_none=True)
    prefix = fields.Str(dump_only=True)
    token = fields.Str(dump_only=True)
    token_hash = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    last_used_at = fields.DateTime(dump_only=True)
    revoked_at = fields.DateTime(allow_none=True)

    user = Relationship(
        self_view='v1.api_key_user',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_detail',
        related_view_kwargs={'api_key_id': '<id>'},
        schema='UserSchema',
        type_='user',
    )
