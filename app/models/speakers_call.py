from sqlalchemy.orm import backref

from app.models import db
from app.models.base import SoftDeletionModel


class SpeakersCall(SoftDeletionModel):
    """call for paper model class"""

    __tablename__ = 'speakers_calls'
    id = db.Column(db.Integer, primary_key=True)
    announcement = db.Column(db.Text, nullable=True)
    starts_at = db.Column(db.DateTime(timezone=True), nullable=False)
    soft_ends_at = db.Column(db.DateTime(timezone=True), nullable=True)
    ends_at = db.Column(db.DateTime(timezone=True), nullable=False)
    hash = db.Column(db.String, nullable=True)
    privacy = db.Column(db.String, nullable=False, default='public')
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship("Event", backref=backref("speakers_call", uselist=False))

    def __repr__(self):
        return '<speakers_call %r>' % self.announcement
