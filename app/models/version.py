from sqlalchemy.orm import backref

from app.models import db


class Version(db.Model):
    """Version model class"""
    __tablename__ = 'versions'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    events = db.relationship("Event", backref=backref('version', uselist=False))

    event_ver = db.Column(db.Integer, nullable=False, default=0)
    sessions_ver = db.Column(db.Integer, nullable=False, default=0)
    speakers_ver = db.Column(db.Integer, nullable=False, default=0)
    tracks_ver = db.Column(db.Integer, nullable=False, default=0)
    sponsors_ver = db.Column(db.Integer, nullable=False, default=0)
    microlocations_ver = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self,
                 event_id=None,
                 event_ver=None,
                 sessions_ver=None,
                 speakers_ver=None,
                 tracks_ver=None,
                 sponsors_ver=None,
                 microlocations_ver=None):
        self.event_id = event_id
        self.event_ver = event_ver
        self.sessions_ver = sessions_ver
        self.speakers_ver = speakers_ver
        self.tracks_ver = tracks_ver
        self.sponsors_ver = sponsors_ver
        self.microlocations_ver = microlocations_ver

    def __repr__(self):
        return '<Version %r>' % self.id

    def __str__(self):
        return self.__repr__()

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'version': [
                {'id': self.id,
                 'event_id': self.event_id,
                 'event_ver': self.event_ver,
                 'sessions_ver': self.sessions_ver,
                 'speakers_ver': self.speakers_ver,
                 'tracks_ver': self.tracks_ver,
                 'sponsors_ver': self.sponsors_ver,
                 'microlocations_ver': self.microlocations_ver}
            ]
        }
