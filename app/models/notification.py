from sqlalchemy_utils import generic_relationship, generic_repr

from app.models import db
from app.models.helpers.timestamp import Timestamp


class NotificationType:
    TICKET_PURCHASED = 'ticket_purchased'
    TICKET_PURCHASED_ATTENDEE = 'ticket_purchased_attendee'
    TICKET_PURCHASED_ORGANIZER = 'ticket_purchased_organizer'
    TICKET_CANCELLED = 'ticket_cancelled'
    TICKET_CANCELLED_ORGANIZER = 'ticket_cancelled_organizer'
    EVENT_ROLE = 'event_role'
    NEW_SESSION = 'new_session'
    SESSION_STATE_CHANGE = 'session_state_change'
    MONTHLY_PAYMENT = 'monthly_payment'
    MONTHLY_PAYMENT_FOLLOWUP = 'monthly_payment'

    @staticmethod
    def entries():
        # Extract all values of defined entries after filtering internal keys
        return list(
            map(
                lambda entry: entry[1],
                filter(
                    lambda entry: not entry[0].startswith('__') and type(entry[1]) == str,
                    NotificationType.__dict__.items(),
                ),
            )
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
        'NotificationContent', backref='actors', foreign_keys=[content_id]
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

    is_read = db.Column(db.Boolean, nullable=False, default=False, server_default='False')

    content_id = db.Column(
        db.Integer,
        db.ForeignKey('notification_content.id', ondelete='CASCADE'),
        nullable=False,
    )
    content = db.relationship(
        'NotificationContent', backref='content', foreign_keys=[content_id]
    )
