from sqlalchemy.orm import backref

from app.models import db
from app.models.base import SoftDeletionModel


class SpeakersCall(SoftDeletionModel):
    """call for paper model class"""
    __tablename__ = 'speakers_calls'
    id = db.Column(db.Integer, primary_key=True)
    announcement = db.Column(db.Text, nullable=False)
    starts_at = db.Column(db.DateTime(timezone=True), nullable=False)
    ends_at = db.Column(db.DateTime(timezone=True), nullable=False)
    hash = db.Column(db.String, nullable=True)
    privacy = db.Column(db.String, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship("Event", backref=backref("speakers_call", uselist=False))

    def __init__(self, announcement=None, starts_at=None, ends_at=None, hash=None, privacy='public',
                 event_id=None, deleted_at=None):
        self.announcement = announcement
        self.starts_at = starts_at
        self.ends_at = ends_at
        self.hash = hash
        self.privacy = privacy
        self.event_id = event_id
        self.deleted_at = deleted_at

    def __repr__(self):
        return '<speakers_call %r>' % self.announcement

    def __str__(self):
        return self.__repr__()

    @property
    def serialize(self):
        """Return object data in easily serializable format"""

        return {
            'id': self.id,
            'announcement': self.announcement,
            'starts_at': self.starts_at.strftime("%Y-%m-%dT%H:%M:%S%Z") if self.starts_at else '',
            'ends_at': self.ends_at.strftime("%Y-%m-%dT%H:%M:%S%Z") if self.ends_at else '',
            'privacy': self.privacy,
            'hash': self.hash
        }
