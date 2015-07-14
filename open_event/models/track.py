"""Copyright 2015 Rafal Kowalski"""
from . import db


class Track(db.Model):
    __tablename__ = 'tracks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    track_image_url = db.Column(db.Text)
    sessions = db.relationship('Session', backref='track', lazy='dynamic')
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))

    def __init__(self, name=None, description=None, event_id=None, session=None, track_image_url=None):
        self.name = name
        self.description = description
        self.event_id = event_id
        self.session_id = session
        self.track_image_url = track_image_url

    def __repr__(self):
        return '<Track %r>' % (self.name)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'description': self.description,
                'track_image_url': self.track_image_url}
