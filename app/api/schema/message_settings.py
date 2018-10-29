from marshmallow_jsonapi import fields
from marshmallow import validate as validate
from marshmallow_jsonapi.flask import Schema

from utils.common import use_defaults
from app.api.helpers.utilities import dasherize

USER_REGISTER = 'User Registration'
USER_CONFIRM = 'User Confirmation'
USER_CHANGE_EMAIL = "User email"
INVITE_PAPERS = 'Invitation For Papers'
NEXT_EVENT = 'Next Event'
NEW_SESSION = 'New Session Proposal'
PASSWORD_RESET = 'Reset Password'
PASSWORD_CHANGE = 'Change Password'
EVENT_ROLE = 'Event Role Invitation'
SESSION_ACCEPT_REJECT = 'Session Accept or Reject'
SESSION_SCHEDULE = 'Session Schedule Change'
EVENT_PUBLISH = 'Event Published'
AFTER_EVENT = 'After Event'
USER_REGISTER_WITH_PASSWORD = 'User Registration during Payment'
TICKET_PURCHASED = 'Ticket(s) Purchased'
TICKET_PURCHASED_ATTENDEE = 'Ticket(s) purchased to Attendee    '
TICKET_PURCHASED_ORGANIZER = 'Ticket(s) Purchased to Organizer'
TICKET_CANCELLED = 'Ticket(s) cancelled'
EVENT_EXPORTED = 'Event Exported'
EVENT_EXPORT_FAIL = 'Event Export Failed'
MAIL_TO_EXPIRED_ORDERS = 'Mail Expired Orders'
MONTHLY_PAYMENT_EMAIL = 'Monthly Payment Email'
MONTHLY_PAYMENT_FOLLOWUP_EMAIL = 'Monthly Payment Follow Up Email'
EVENT_IMPORTED = 'Event Imported'
EVENT_IMPORT_FAIL = 'Event Import Failed'


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
        allow_none=True, dump_only=True,
        validate=validate.OneOf(
            choices=[INVITE_PAPERS, NEW_SESSION, USER_CONFIRM, USER_REGISTER,
                     PASSWORD_RESET, EVENT_ROLE, SESSION_ACCEPT_REJECT,
                     SESSION_SCHEDULE, NEXT_EVENT, EVENT_PUBLISH, AFTER_EVENT,
                     USER_CHANGE_EMAIL, USER_REGISTER_WITH_PASSWORD,
                     TICKET_PURCHASED, EVENT_EXPORTED, EVENT_EXPORT_FAIL,
                     MAIL_TO_EXPIRED_ORDERS, MONTHLY_PAYMENT_EMAIL,
                     MONTHLY_PAYMENT_FOLLOWUP_EMAIL, EVENT_IMPORTED,
                     EVENT_IMPORT_FAIL, TICKET_PURCHASED_ORGANIZER,
                     TICKET_CANCELLED, TICKET_PURCHASED_ATTENDEE,
                     PASSWORD_CHANGE]
        ))
    mail_status = fields.Boolean(default=False)
    notification_status = fields.Boolean(default=False)
    user_control_status = fields.Boolean(default=False)
    email_message = fields.Str(dump_only=True)
    recipient = fields.Str(dump_only=True)
    email_subject = fields.Str(dump_only=True)
    notification_title = fields.Str(dump_only=True)
    notification_message = fields.Str(dump_only=True)
    sent_at = fields.DateTime(dump_only=True)
