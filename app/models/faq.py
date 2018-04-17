from __future__ import unicode_literals

from future.utils import python_2_unicode_compatible

from app.models import db
from utils.compat import u


@python_2_unicode_compatible
class Faq(db.Model):
    """Page model class"""
    __tablename__ = 'faq'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String, nullable=False)
    answer = db.Column(db.String, nullable=False)
    event_id = db.Column(db.Integer,
                         db.ForeignKey('events.id', ondelete='CASCADE'))
    faq_type_id = db.Column(db.Integer, db.ForeignKey('faq_types.id', ondelete='CASCADE'))

    def __init__(self, question=None, answer=None, event_id=None, faq_type_id=None):
        self.question = question
        self.answer = answer
        self.event_id = event_id
        self.faq_type_id = faq_type_id

    def __repr__(self):
        return '<FAQ %r>' % self.question

    def __str__(self):
        return u(self.question)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer
        }
