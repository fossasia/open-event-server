from datetime import datetime
import pytz

from app.models import db
from app.models.base import SoftDeletionModel


class EventChatMessage(SoftDeletionModel):
    """Event User Message
    """
    __tablename__ = 'event_chat_message'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',
                                                  ondelete='CASCADE'))
    user = db.relationship('User')
    event_id = db.Column(db.Integer, db.ForeignKey('events.id',
                                                   ondelete='CASCADE'))
    message = db.Column(db.String, nullable=False)
    timezone = db.Column(db.String, nullable=False, default="UTC")
    sent_at = db.Column(db.DateTime(timezone=True))

    def __init__(self, user=None, event=None, message=None,
                 user_id=None, event_id=None, timezone=None):
        self.user = user
        self.message = message
        self.user_id = user_id
        self.event_id = event_id
        self.timezone = timezone
        self.sent_at = datetime.now(pytz.utc)

    def __str__(self):
        return '%r as %r' % (self.user, self.message)
