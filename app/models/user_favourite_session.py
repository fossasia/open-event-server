from datetime import datetime

from app.models import db


class UserFavouriteSession(db.Model):
    __tablename__ = 'user_favourite_sessions'
    __table_args__ = (
        db.UniqueConstraint('session_id', 'user_id', name='uq_session_user'),
    )

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    created_at: datetime = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    modified_at: datetime = db.Column(
        db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    session = db.relationship('Session', backref='favourite_sessions')
