from marshmallow import validate
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema, TrimmedEmail


class UserEmailSchema(SoftDeletionSchema):
    """
    API Schema for user email Model
    """

    class Meta:
        """
        Meta class for user email API schema
        """

        type_ = 'user-email'
        self_view = 'v1.user_emails_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str()
    email_address = TrimmedEmail(allow_none=False)
    type = fields.Str(
        allow_none=False,
        validate=validate.OneOf(choices=["home", "work", "business", "office", "other"]),
    )
    user_id = fields.Integer(allow_none=False)
    user = Relationship(
        self_view='v1.user_emails_user',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_detail',
        related_view_kwargs={'user_email_id': '<id>'},
        schema='UserSchema',
        type_='user',
    )
