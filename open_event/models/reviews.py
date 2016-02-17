from . import db
from .session import Session

class Review(db.Model):
    """Review model class"""
    __tablename__ = 'session_reviews'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False)
    comment = db.Column(db.String)
    rating = db.Column(db.Integer, nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))
    
    def __init__(self,
                 email=None,
                 comment=None,
                 rating=None,
                 session_id=None):
        self.email = email
        self.comment = comment
        self.rating = rating
        self.session_id = session_id

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'email': self.email,
                'comment': self.comment,
                'rating': self.rating,
                'session_id': self.session_id}

    def __repr__(self):
        return '<Review %r>' % (self.id)