from sqlalchemy.orm import backref

from app.models import db
from app.models.base import SoftDeletionModel


class EventCopyright(SoftDeletionModel):
    """
    Copyright Information about an event.
    """

    __tablename__ = 'event_copyrights'

    id = db.Column(db.Integer, primary_key=True)
    holder = db.Column(db.String)
    holder_url = db.Column(db.String)
    licence = db.Column(db.String, nullable=False)
    licence_url = db.Column(db.String)
    year = db.Column(db.Integer)
    logo = db.Column(db.String)

    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship('Event', backref=backref('copyright', uselist=False))

    def __repr__(self):
        return '<Copyright %r>' % self.holder
