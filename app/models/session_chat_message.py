from datetime import datetime
import pytz

from app.models import db
from app.models.base import SoftDeletionModel


class SessionChatMessage(SoftDeletionModel):
    """Session User Message
    """
    __tablename__ = 'session_chat_message'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',
                                                  ondelete='CASCADE'))
    user = db.relationship('User')
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id',
                                                     ondelete='CASCADE'))
    message = db.Column(db.String, nullable=False)
    timezone = db.Column(db.String, nullable=False, default="UTC")
    sent_at = db.Column(db.DateTime(timezone=True))
    label = db.Column(db.String, nullable=False)

    def __init__(self, user=None, session=None, message=None, label=None,
                 user_id=None, session_id=None, timezone=None):
        self.user = user
        self.session = session
        self.message = message
        self.user_id = user_id
        self.session_id = session_id
        self.timezone = timezone
        self.sent_at = datetime.now(pytz.utc)
        self.label = label

    def __str__(self):
        return '%r as %r' % (self.user, self.message)
