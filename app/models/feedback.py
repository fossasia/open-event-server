from app.models import db


class Feedback(db.Model):
    """Feedback model class"""
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.String, nullable=False)
    comment = db.Column(db.String, nullable=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id', ondelete='CASCADE'))
    event_id = db.Column(db.Integer,
                         db.ForeignKey('events.id', ondelete='CASCADE'))

    def __init__(self, rating=None, comment=None, event_id=None, user_id=None):
        self.rating = rating
        self.comment = comment
        self.event_id = event_id
        self.user_id = user_id

    def __repr__(self):
        return '<Feedback %r>' % self.rating

    def __str__(self):
        return self.__repr__()

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'rating': self.rating,
            'comment': self.comment
        }
