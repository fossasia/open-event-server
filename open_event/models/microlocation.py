"""Copyright 2015 Rafal Kowalski"""
from . import db


class Microlocation(db.Model):
    __tablename__ = 'microlocations'
    id = db.Column(db.Integer,
                   primary_key=True)
    name = db.Column(db.String,
                     nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    floor = db.Column(db.Integer)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))
    event_id = db.Column(db.Integer,
                         db.ForeignKey('events.id'))

    def __init__(self,
                 name=None,
                 latitude=None,
                 longitude=None,
                 floor=None,
                 event_id=None):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.floor = floor
        self.event_id = event_id

    def __repr__(self):
        return '<Microlocation %r>' % (self.name)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'latitude': self.latitude,
                'longitude': self.longitude,
                'floor': self.floor}
