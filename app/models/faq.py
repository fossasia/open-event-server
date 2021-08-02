from app.models import db
from app.models.base import SoftDeletionModel


class Faq(SoftDeletionModel):
    """Page model class"""

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String, nullable=False)
    answer = db.Column(db.String, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    faq_type_id = db.Column(db.Integer, db.ForeignKey('faq_types.id', ondelete='CASCADE'))

    def __repr__(self):
        return '<FAQ %r>' % self.question
