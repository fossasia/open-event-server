"""Copyright 2015 Rafal Kowalski"""
from open_event.helpers.date_formatter import DateFormatter
from . import db
from sqlalchemy_utils import ColorType


class EventsUsers(db.Model):
    """Many to Many table Event Users"""
    __tablename__ = 'eventsusers'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    editor = db.Column(db.Boolean)
    admin = db.Column(db.Boolean)
    user = db.relationship("User", backref="events_assocs")
    role = db.Column(db.String, nullable=False)


class Event(db.Model):
    """Event object table"""
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String)
    color = db.Column(ColorType)
    logo = db.Column(db.String)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    location_name = db.Column(db.String)
    description = db.Column(db.Text)
    event_url = db.Column(db.String)
    background_url = db.Column(db.String)
    organizer_name = db.Column(db.String)
    organizer_description = db.Column(db.String)
    track = db.relationship('Track', backref="event")
    microlocation = db.relationship('Microlocation', backref="event")
    session = db.relationship('Session', backref="event")
    speaker = db.relationship('Speaker', backref="event")
    sponsor = db.relationship('Sponsor', backref="event")
    users = db.relationship("EventsUsers", backref="event")

    roles = db.relationship("UsersEventsRoles", backref="event")
    state = db.Column(db.String, default="Draft")
    closing_datetime = db.Column(db.DateTime)

    db.UniqueConstraint('track.name')

    def __init__(self,
                 name=None,
                 logo=None,
                 start_time=None,
                 end_time=None,
                 latitude=None,
                 longitude=None,
                 location_name=None,
                 email=None,
                 color=None,
                 description=None,
                 event_url=None,
                 background_url=None,
                 organizer_name=None,
                 organizer_description=None,
                 state=None,
                 closing_datetime=None):
        self.name = name
        self.logo = logo
        self.email = email
        self.color = color
        self.start_time = start_time
        self.end_time = end_time
        self.latitude = latitude
        self.longitude = longitude
        self.location_name = location_name
        self.description = description
        self.event_url = event_url
        self.background_url = background_url
        self.organizer_name = organizer_name
        self.organizer_description = organizer_description
        self.state = state
        self.closing_datetime = closing_datetime
        # self.owner = owner

    def __repr__(self):
        return '<Event %r>' % self.name

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.name

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'logo': self.logo,
            'begin': DateFormatter().format_date(self.start_time),
            'end': DateFormatter().format_date(self.end_time),
            'latitude': self.latitude,
            'longitude': self.longitude,
            'location_name': self.location_name,
            'email': self.email,
            'color': self.color.get_hex() if self.color else '',
            'description': self.description,
            'event_url': self.event_url,
            'background_url': self.background_url,
            'organizer_name': self.organizer_name,
            'organizer_description': self.organizer_description
        }
