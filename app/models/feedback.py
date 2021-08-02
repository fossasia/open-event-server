from app.models import db
from app.models.base import SoftDeletionModel


class Feedback(SoftDeletionModel):
    """Feedback model class"""

    __tablename__ = 'feedback'
    __table_args__ = (
        db.UniqueConstraint('session_id', 'user_id', name='session_user_uc'),
    )

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Float, nullable=False)
    comment = db.Column(db.String, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id', ondelete='CASCADE'))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # TODO(Areeb): Test rating rounding on __init__
        rating = float(kwargs.get('rating'))
        self.rating = round(rating * 2, 0) / 2  # Rounds to nearest 0.5

    def __repr__(self):
        return '<Feedback %r>' % self.rating
