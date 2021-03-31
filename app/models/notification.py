from sqlalchemy_utils import generic_relationship, generic_repr

from app.models import db
from app.models.helpers.timestamp import Timestamp

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
SESSION_STATE_CHANGE = 'Session State Change'
INVITE_PAPERS = 'Invitation For Papers'
AFTER_EVENT = 'After Event'
EVENT_PUBLISH = 'Event Published'
TICKET_PURCHASED_ORGANIZER = 'Ticket(s) Purchased to Organizer'
TICKET_RESEND_ORGANIZER = 'Ticket Resend'
TICKET_CANCELLED = 'Ticket(s) cancelled'
TICKET_CANCELLED_ORGANIZER = 'Ticket(s) cancelled organizer'
MONTHLY_PAYMENT_NOTIF = 'Monthly Payment Notification'
MONTHLY_PAYMENT_FOLLOWUP_NOTIF = 'Monthly Payment Follow Up Notification'


class NotificationAction(db.Model):
    """
    Model for storing user notification actions.
    """

    __tablename__ = 'notification_actions'

    id = db.Column(db.Integer, primary_key=True)

    action_type = db.Column(db.String)
    subject = db.Column(db.String)
    subject_id = db.Column(
        db.String
    )  # Contains the ID of the related subject, eg. session_id in case of new session.
    link = db.Column(
        db.String
    )  # Contains the link if required to take action. Null in other cases.

    notification_id = db.Column(
        db.Integer, db.ForeignKey('notifications.id', ondelete='CASCADE')
    )
    notification = db.relationship(
        'Notification', backref='actions', foreign_keys=[notification_id]
    )


@generic_repr
class NotificationActor(db.Model, Timestamp):

    __tablename__ = 'notification_actors'

    id = db.Column(db.Integer, primary_key=True)

    actor_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False
    )
    actor = db.relationship(
        'User', backref='notification_actors', foreign_keys=[actor_id]
    )

    content_id = db.Column(
        db.Integer,
        db.ForeignKey('notification_content.id', ondelete='CASCADE'),
        nullable=False,
    )
    content = db.relationship(
        'NotificationContent', backref='actor', foreign_keys=[content_id]
    )


@generic_repr
class NotificationContent(db.Model, Timestamp):

    __tablename__ = 'notification_content'

    id = db.Column(db.Integer, primary_key=True)

    type = db.Column(db.String, nullable=False)

    target_type = db.Column(db.Unicode(255))
    target_id = db.Column(db.Integer)
    target = generic_relationship(target_type, target_id)

    # For storing state of the action
    target_action = db.Column(db.String)


@generic_repr
class Notification(db.Model, Timestamp):
    """
    Model for storing user notifications.
    """

    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False
    )
    user = db.relationship('User', backref='notifications', foreign_keys=[user_id])

    received_at = db.Column(db.DateTime(timezone=True))
    is_read = db.Column(db.Boolean)

    content_id = db.Column(
        db.Integer,
        db.ForeignKey('notification_content.id', ondelete='CASCADE'),
        nullable=False,
    )
    content = db.relationship(
        'NotificationContent', backref='content', foreign_keys=[content_id]
    )
