from datetime import datetime
from enum import Enum, unique

import pytz

from app.models import db
from app.models.base import SoftDeletionModel

USER_CHANGE_EMAIL = "User email"
PASSWORD_CHANGE = 'Change Password'
TICKET_PURCHASED = 'Ticket(s) Purchased'
TICKET_PURCHASED_ATTENDEE = 'Ticket Purchased to Attendee'
EVENT_ROLE = 'Event Role Invitation'
NEW_SESSION = 'New Session Proposal'
EVENT_EXPORT_FAIL = 'Event Export Failed'
EVENT_EXPORTED = 'Event Exported'
EVENT_IMPORT_FAIL = 'Event Import Failed'
EVENT_IMPORTED = 'Event Imported'
SESSION_SCHEDULE = 'Session Schedule Change'
NEXT_EVENT = 'Next Event'
SESSION_ACCEPT_REJECT = 'Session Accept or Reject'
INVITE_PAPERS = 'Invitation For Papers'
AFTER_EVENT = 'After Event'
EVENT_PUBLISH = 'Event Published'
TICKET_PURCHASED_ORGANIZER = 'Ticket(s) Purchased to Organizer'
TICKET_RESEND_ORGANIZER = 'Ticket Resend'
TICKET_CANCELLED = 'Ticket(s) cancelled'
TICKET_CANCELLED_ORGANIZER = 'Ticket(s) cancelled organizer'
MONTHLY_PAYMENT_NOTIF = 'Monthly Payment Notification'
MONTHLY_PAYMENT_FOLLOWUP_NOTIF = 'Monthly Payment Follow Up Notification'


@unique
class NotificationTopic(Enum):
    """
    Enum class used to link a Notification to it's actions.
    """
    USER_CHANGE_EMAIL = 0
    PASSWORD_CHANGE = 1
    TICKET_PURCHASED = 2
    TICKET_PURCHASED_ATTENDEE = 3
    EVENT_ROLE = 4
    NEW_SESSION = 5
    EVENT_EXPORT_FAIL = 6
    EVENT_EXPORTED = 7
    EVENT_IMPORT_FAIL = 8
    EVENT_IMPORTED = 9
    SESSION_SCHEDULE = 10
    NEXT_EVENT = 11
    SESSION_ACCEPT_REJECT = 12
    INVITE_PAPERS = 13
    AFTER_EVENT = 14
    EVENT_PUBLISH = 15
    TICKET_PURCHASED_ORGANIZER = 16
    TICKET_RESEND_ORGANIZER = 17
    TICKET_CANCELLED = 18
    TICKET_CANCELLED_ORGANIZER = 19
    MONTHLY_PAYMENT_NOTIF = 20
    MONTHLY_PAYMENT_FOLLOWUP_NOTIF = 21


class NotificationActions(db.Model):
    """
        Model for storing user notification actions.
    """
    __tablename__ = 'notification_actions'

    id = db.Column(db.Integer, primary_key=True)

    action_type = db.Column(db.String)
    subject = db.Column(db.String)
    notification_topic = db.Column(db.Integer)

    def __init__(self, action_type=None, subject=None, notification_topic=None):
        self.action_type = action_type
        self.subject = subject
        self.notification_topic = notification_topic


class Notification(SoftDeletionModel):
    """
        Model for storing user notifications.
    """
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User', backref='notifications', foreign_keys=[user_id])

    title = db.Column(db.String)
    message = db.Column(db.Text)
    received_at = db.Column(db.DateTime(timezone=True))
    is_read = db.Column(db.Boolean)
    subject_id = db.Column(db.Integer)  # Contains the ID of the related subject, eg. session_id in case of new session.
    notification_topic = db.Column(db.Integer)

    def __init__(self, user_id=None, title=None, message=None, is_read=False, deleted_at=None, subject_id=None,
                 notification_topic=None):
        self.user_id = user_id
        self.title = title
        self.message = message
        self.received_at = datetime.now(pytz.utc)
        self.is_read = is_read
        self.deleted_at = deleted_at
        self.subject_id = subject_id
        self.notification_topic = notification_topic

    def __repr__(self):
        return '<Notif %s:%s>' % (self.user, self.title)

    def __str__(self):
        return self.__repr__()

    @property
    def actions(self):
        """
        Returns the actions associated with a notification.
        """
        return db.session.query(NotificationActions).filter_by(notification_topic=self.notification_topic)
