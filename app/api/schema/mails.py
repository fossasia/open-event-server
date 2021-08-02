from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from app.api.helpers.utilities import dasherize
from app.api.schema.base import TrimmedEmail


class MailSchema(Schema):
    """
    Api schema for mail Model
    """

    class Meta:
        """
        Meta class for mail Api Schema
        """

        type_ = 'mail'
        self_view = 'v1.mail_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'v1.mail_list'
        inflect = dasherize

    id = fields.Str(dump_only=True)
    recipient = TrimmedEmail(dump_only=True)
    time = fields.DateTime(dump_only=True)
    action = fields.Str(dump_only=True)
    subject = fields.Str(dump_only=True)
    message = fields.Str(dump_only=True)
