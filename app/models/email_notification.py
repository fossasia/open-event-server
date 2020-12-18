from app.models import db
from app.models.base import SoftDeletionModel


class EmailNotification(SoftDeletionModel):
    """email notifications model class"""

    __tablename__ = 'email_notifications'
    id = db.Column(db.Integer, primary_key=True)
    next_event = db.Column(db.Boolean, default=False)
    new_paper = db.Column(db.Boolean, default=False)
    session_accept_reject = db.Column(db.Boolean, default=False)
    session_schedule = db.Column(db.Boolean, default=False)
    after_ticket_purchase = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship("Event")
    user = db.relationship("User", backref="email_notifications")

    def __str__(self):
        return 'User:' + self.user_id + ' Event: ' + self.event_id
