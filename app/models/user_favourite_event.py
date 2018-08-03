from app.models import db


class UserFavouriteEvent(db.Model):
    __tablename__ = 'user_favourite_events'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    event = db.relationship("Event")

    def __init__(self, user=None, event=None, user_id=None, event_id=None):
        self.user = user
        self.event = event
        self.user_id = user_id
        self.event_id = event_id
