__author__ = 'rafal'
from . import db
from ..date_formatter import DateFormatter


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String)
    color = db.Column(db.String)
    logo = db.Column(db.String)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    location_name = db.Column(db.String)
    track = db.relationship('Track', backref="event")
    microlocation = db.relationship('Microlocation', backref="event")
    session = db.relationship('Session', backref="event")
    speaker = db.relationship('Speaker', backref="event")
    sponsor = db.relationship('Sponsor', backref="event")

    def __init__(self,
                 name=None,
                 logo=None,
                 start_time=None,
                 end_time=None,
                 latitude=None,
                 longitude=None,
                 location_name=None,
                 email=None,
                 color=None):
        self.name = name
        self.logo = logo
        self.email = email
        self.color = color
        self.start_time = start_time
        self.end_time = end_time
        self.latitude = latitude
        self.longitude = longitude
        self.location_name = location_name

    def __repr__(self):
        return '<Event %r>' % (self.name)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'logo': self.logo,
                'start_time': DateFormatter().format_date(self.start_time),
                'end_time': DateFormatter().format_date(self.end_time),
                'latitude': self.latitude,
                'longitude': self.longitude,
                'location_name': self.location_name,
                'email': self.email,
                'color': self.color}
