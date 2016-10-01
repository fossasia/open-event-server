"""Copyright 2015 Rafal Kowalski"""
from . import db


class Track(db.Model):
    """Track model class"""
    __tablename__ = 'tracks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    track_image_url = db.Column(db.Text)
    color = db.Column(db.String, nullable=False)
    location = db.Column(db.String)
    sessions = db.relationship('Session', backref='track', lazy='dynamic')
    event_id = db.Column(
        db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))

    def __init__(self, name=None, description=None, event_id=None,
                 session=None, track_image_url=None, color=None,
                 location=None):
        self.name = name
        self.description = description
        self.event_id = event_id
        self.session_id = session
        self.track_image_url = track_image_url
        self.color = color
        self.location = location

    @staticmethod
    def get_service_name():
        return 'track'

    def __repr__(self):
        return '<Track %r>' % self.name

    def __str__(self):
        return str(self).encode('utf-8')

    def __unicode__(self):
        return self.name

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        sessions = [{'id': session.id, 'title': session.title}
                    for session in self.sessions]
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'sessions': sessions,
            'track_image_url': self.track_image_url,
            'color': self.color
        }
