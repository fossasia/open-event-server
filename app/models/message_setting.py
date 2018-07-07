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
    def _email_message(self, action):
        message = {}
        if action == EVENT_PUBLISH:
            message = MAILS[EVENT_PUBLISH]
        elif action == INVITE_PAPERS:
            message = MAILS[INVITE_PAPERS]
        elif action == SESSION_ACCEPT_REJECT:
            message = MAILS[SESSION_ACCEPT_REJECT]
        elif action == SESSION_SCHEDULE:
            message = MAILS[SESSION_SCHEDULE]
        elif action == NEXT_EVENT:
            message = MAILS[NEXT_EVENT]
        elif action == AFTER_EVENT:
            message = MAILS[AFTER_EVENT]
        elif action == NEW_SESSION:
            message = MAILS[NEW_SESSION]
        elif action == USER_REGISTER:
            message = MAILS[USER_REGISTER]
        elif action == USER_REGISTER_WITH_PASSWORD:
            message = MAILS.USER_REGISTER_WITH_PASSWORD
        elif action == USER_CONFIRM:
            message = MAILS[USER_CONFIRM]
        elif action == USER_CHANGE_EMAIL:
            message = MAILS.USER_CHANGE_EMAIL
        elif action == PASSWORD_RESET:
            message = MAILS[PASSWORD_RESET]
        elif action == PASSWORD_CHANGE:
            message = MAILS.PASSWORD_CHANGE
        elif action == EVENT_ROLE:
            message = MAILS[EVENT_ROLE]
        elif action == TICKET_PURCHASED:
            message = MAILS.TICKET_PURCHASED
        elif action == TICKET_PURCHASED_ATTENDEE:
            message = MAILS.TICKET_PURCHASED_ATTENDEE
        elif action == TICKET_PURCHASED_ORGANIZER:
            message = MAILS.TICKET_PURCHASED_ORGANIZER
        elif action == TICKET_CANCELLED:
            message = MAILS.TICKET_CANCELLED
        elif action == EVENT_EXPORTED:
            message = MAILS.EVENT_EXPORTED
        elif action == EVENT_EXPORT_FAIL:
            message = MAILS.EVENT_EXPORT_FAIL
        elif action == MAIL_TO_EXPIRED_ORDERS:
            message = MAILS.MAIL_TO_EXPIRED_ORDERS
        elif action == MONTHLY_PAYMENT_EMAIL:
            message = MAILS.MONTHLY_PAYMENT_EMAIL
        elif action == MONTHLY_PAYMENT_FOLLOWUP_EMAIL:
            message = MAILS.MONTHLY_PAYMENT_FOLLOWUP_EMAIL
        elif action == EVENT_IMPORTED:
            message = MAILS.EVENT_IMPORTED
        elif action == EVENT_IMPORT_FAIL:
            message = MAILS.EVENT_IMPORT_FAIL
        else:
            message = "No Email was sent"
        return message

    @hybrid_property
    def email_message(self):
        message = self._email_message(self.action)
        return message

    @classmethod
    def _notification_message(self, action):
        message = {}
        if action == EVENT_PUBLISH:
            message = NOTIFS[EVENT_PUBLISH]
        elif action == INVITE_PAPERS:
            message = NOTIFS[INVITE_PAPERS]
        elif action == SESSION_ACCEPT_REJECT:
            message = NOTIFS[SESSION_ACCEPT_REJECT]
        elif action == SESSION_SCHEDULE:
            message = NOTIFS[SESSION_SCHEDULE]
        elif action == NEXT_EVENT:
            message = NOTIFS[NEXT_EVENT]
        elif action == AFTER_EVENT:
            message = NOTIFS[AFTER_EVENT]
        elif action == NEW_SESSION:
            message = NOTIFS[NEW_SESSION]
        elif action == USER_REGISTER_WITH_PASSWORD:
            message = NOTIFS.USER_REGISTER_WITH_PASSWOR
        elif action == USER_CHANGE_EMAIL:
            message = NOTIFS.USER_CHANGE_EMAIL
        elif action == PASSWORD_RESET:
            message = NOTIFS[PASSWORD_RESET]
        elif action == PASSWORD_CHANGE:
            message = NOTIFS.PASSWORD_CHANGE
        elif action == EVENT_ROLE:
            message = NOTIFS[EVENT_ROLE]
        elif action == TICKET_PURCHASED:
            message = NOTIFS.TICKET_PURCHASED
        elif action == TICKET_PURCHASED_ATTENDEE:
            message = NOTIFS.TICKET_PURCHASED_ATTENDEE
        elif action == TICKET_PURCHASED_ORGANIZER:
            message = NOTIFS.TICKET_PURCHASED_ORGANIZER
        elif action == TICKET_CANCELLED:
            message = NOTIFS.TICKET_CANCELLED
        elif action == EVENT_EXPORTED:
            message = NOTIFS.EVENT_EXPORTED
        elif action == EVENT_EXPORT_FAIL:
            message = NOTIFS.EVENT_EXPORT_FAIL
        elif action == MAIL_TO_EXPIRED_ORDERS:
            message = NOTIFS.MAIL_TO_EXPIRED_ORDERS
        elif action == MONTHLY_PAYMENT_EMAIL:
            message = NOTIFS.MONTHLY_PAYMENT_EMAIL
        elif action == MONTHLY_PAYMENT_FOLLOWUP_EMAIL:
            message = NOTIFS.MONTHLY_PAYMENT_FOLLOWUP_EMAIL
        elif action == EVENT_IMPORTED:
            message = NOTIFS.EVENT_IMPORTED
        elif action == EVENT_IMPORT_FAIL:
            message = NOTIFS.EVENT_IMPORT_FAIL
        else:
            message = "No Notification was sent"
        return message

    @hybrid_property
    def notification_message(self):
        message = self._notification_message(self.action)
        return message

    @property
    def serialize(self):
        """Return object data in easily serializable format"""

        return {'id': self.id,
                'action': self.action,
                'mail_status': self.mail_status,
                'notification_status': self.notification_status,
                'user_control_status': self.user_control_status}
