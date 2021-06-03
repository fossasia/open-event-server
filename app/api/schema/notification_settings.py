from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from app.api.helpers.utilities import dasherize


class NotificationSettingSchema(Schema):
    class Meta:

        type_ = 'notification-setting'
        self_view = 'v1.notification_setting_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    type = fields.Str(dump_only=True)
    enabled = fields.Boolean(default=True)
