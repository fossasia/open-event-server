from app.models import db
from app.models.helpers.timestamp import Timestamp


class UserFavouriteSession(db.Model, Timestamp):
    __tablename__ = 'user_favourite_sessions'
    __table_args__ = (
        db.UniqueConstraint('session_id', 'user_id', name='uq_session_user'),
    )

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    session = db.relationship('Session', backref='favourites')
    user = db.relationship('User', backref='favourite_sessions')
