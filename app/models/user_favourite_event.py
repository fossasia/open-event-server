from app.models import db
from app.models.base import SoftDeletionModel


class UserFavouriteEvent(SoftDeletionModel):
    __tablename__ = 'user_favourite_events'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    event = db.relationship("Event")
