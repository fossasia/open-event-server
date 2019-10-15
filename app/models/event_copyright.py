from sqlalchemy.orm import backref

from dataclasses import dataclass
from app.models import db
from app.models.base import SoftDeletionModel


@dataclass(init=True, repr=True, unsafe_hash=True)
class EventCopyright(SoftDeletionModel):
    """
    Copyright Information about an event.
    """
    __tablename__ = 'event_copyrights'

    id: int = db.Column(db.Integer, primary_key=True)
    holder: str = db.Column(db.String)
    holder_url: str = db.Column(db.String)
    licence: str = db.Column(db.String, nullable=False)
    licence_url: str = db.Column(db.String)
    year: int = db.Column(db.Integer)
    logo: str = db.Column(db.String)

    event_id: int = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship('Event', backref=backref('copyright', uselist=False))

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'holder': self.holder,
            'holder_url': self.holder_url,
            'licence': self.licence,
            'licence_url': self.licence_url,
            'year': self.year,
            'logo': self.logo
        }
