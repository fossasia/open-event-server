from . import db

class Review(db.Model):
    """Review model"""
    __tablename__ = 'review'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    comment = db.Column(db.String)
    rating = db.Column(db.Integer, nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))

    __table_args__ = (db.UniqueConstraint('email', 'session_id',
                      name='_unique_review_id'),)

    def __init__(self, name, email, comment, rating, session_id):
        self.name = name
        self.email = email
        self.comment = comment
        self.rating = rating
        self.session_id = session_id

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'comment': self.comment,
            'rating': self.rating,
        }

    def __repr__(self):
        return 'Review {0} by {1}'.format(self.id, self.name)
