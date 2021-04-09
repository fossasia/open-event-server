from marshmallow import validate
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from app.api.helpers.system_mails import MailType
from app.api.helpers.utilities import dasherize
from utils.common import use_defaults


@use_defaults()
class MessageSettingSchema(Schema):
    """
    API Schema for Message Setting Model
    """

    class Meta:
        """
        Meta class for Message Setting API schema
        """

        type_ = 'message-setting'
        self_view = 'v1.message_setting_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    action = fields.Str(
        allow_none=True,
        dump_only=True,
        validate=validate.OneOf(choices=MailType.entries()),
    )
    enabled = fields.Boolean(default=True)
    email_message = fields.Str(dump_only=True)
    recipient = fields.Str(dump_only=True)
    email_subject = fields.Str(dump_only=True)
