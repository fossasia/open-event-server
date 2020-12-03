from app.models import db
from app.models.base import SoftDeletionModel


class UserFavouriteSession(SoftDeletionModel):
    __tablename__ = 'user_favourite_session'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    session = db.relationship('Session')
