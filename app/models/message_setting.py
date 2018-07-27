from app.models import db
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime

import pytz

from app.api.helpers.system_mails import MAILS
from app.api.helpers.system_notifications import NOTIFS

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
TICKET_PURCHASED_ATTENDEE = 'Ticket(s) purchased to Attendee'
TICKET_PURCHASED_ORGANIZER = 'Ticket(s) Purchased to Organizer'
TICKET_CANCELLED = 'Ticket(s) cancelled'
TICKET_RESEND_ORGANIZER = 'Ticket Resend'
EVENT_EXPORTED = 'Event Exported'
EVENT_EXPORT_FAIL = 'Event Export Failed'
EVENT_IMPORT_FAIL = 'Event Import Failed'
MAIL_TO_EXPIRED_ORDERS = 'Mail Expired Orders'
MONTHLY_PAYMENT_EMAIL = 'Monthly Payment Email'
MONTHLY_PAYMENT_NOTIF = 'Monthly Payment Notification'
MONTHLY_PAYMENT_FOLLOWUP_EMAIL = 'Monthly Payment Follow Up Email'
MONTHLY_PAYMENT_FOLLOWUP_NOTIF = 'Monthly Payment Follow Up Notification'
EVENT_IMPORTED = 'Event Imported'
TICKET_CANCELLED_ORGANIZER = 'Ticket(s) cancelled organizer'


class MessageSettings(db.Model):
    __tablename__ = 'message_settings'
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String)
    mail_status = db.Column(db.Boolean, default=False)
    notification_status = db.Column(db.Boolean, default=False)
    user_control_status = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime(timezone=True))

    def __init__(self, action=None, mail_status=None,
                 notification_status=None, user_control_status=None):
        self.action = action
        self.mail_status = mail_status
        self.notification_status = notification_status
        self.user_control_status = user_control_status
        self.sent_at = datetime.now(pytz.utc)

    def __repr__(self):
        return '<Message Setting %r >' % self.action

    def __str__(self):
        return self.__repr__()

    @classmethod
    def _email_message(self, action, attr=None):
        message = {}
        if action in [INVITE_PAPERS, NEW_SESSION, USER_CONFIRM,
                      USER_REGISTER, PASSWORD_RESET, EVENT_ROLE,
                      SESSION_ACCEPT_REJECT, SESSION_SCHEDULE, NEXT_EVENT,
                      EVENT_PUBLISH, AFTER_EVENT, USER_CHANGE_EMAIL,
                      USER_REGISTER_WITH_PASSWORD, TICKET_PURCHASED,
                      EVENT_EXPORTED, EVENT_EXPORT_FAIL,
                      MAIL_TO_EXPIRED_ORDERS, MONTHLY_PAYMENT_EMAIL,
                      MONTHLY_PAYMENT_FOLLOWUP_EMAIL, EVENT_IMPORTED,
                      EVENT_IMPORT_FAIL, TICKET_PURCHASED_ORGANIZER,
                      TICKET_CANCELLED, TICKET_PURCHASED_ATTENDEE,
                      PASSWORD_CHANGE]:
            message = MAILS[action]
        else:
            message = MAILS.__dict__[action]
        message = str(message.get(attr))
        return message

    @hybrid_property
    def email_message(self):
        message = self._email_message(self.action, attr='message')
        return message

    @hybrid_property
    def recipient(self):
        message = self._email_message(self.action, attr='recipient')
        return message

    @hybrid_property
    def email_subject(self):
        message = self._email_message(self.action, attr='subject')
        return message

    @classmethod
    def _notification_message(self, action, attr=None):
        message = {}
        if action in [EVENT_ROLE, NEW_SESSION, SESSION_SCHEDULE,
                      NEXT_EVENT, SESSION_ACCEPT_REJECT, INVITE_PAPERS,
                      AFTER_EVENT, EVENT_PUBLISH, USER_CHANGE_EMAIL,
                      PASSWORD_CHANGE, TICKET_PURCHASED,
                      TICKET_RESEND_ORGANIZER, EVENT_EXPORT_FAIL,
                      EVENT_EXPORTED, EVENT_IMPORT_FAIL, EVENT_IMPORTED,
                      MONTHLY_PAYMENT_NOTIF, MONTHLY_PAYMENT_FOLLOWUP_NOTIF,
                      TICKET_PURCHASED_ORGANIZER, TICKET_PURCHASED_ATTENDEE,
                      TICKET_CANCELLED, TICKET_CANCELLED_ORGANIZER]:
            message = NOTIFS[action]
        else:
            message = NOTIFS.__dict__[action]
        message = str(message.get(attr))
        return message

    @hybrid_property
    def notification_message(self):
        message = self._notification_message(self.action, attr='message')
        return message

    @hybrid_property
    def notification_title(self):
        message = self._notification_message(self.action, attr='title')
        return message

    @property
    def serialize(self):
        """Return object data in easily serializable format"""

        return {'id': self.id,
                'action': self.action,
                'mail_status': self.mail_status,
                'notification_status': self.notification_status,
                'user_control_status': self.user_control_status}
