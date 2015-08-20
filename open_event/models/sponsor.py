"""Copyright 2015 Rafal Kowalski"""
from . import db


class Sponsor(db.Model):
    """Sponsor model class"""
    __tablename__ = 'sponsors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    url = db.Column(db.String)
    logo = db.Column(db.String)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))

    def __init__(self, name=None, url=None, logo=None, event_id=None):
        self.name = name
        self.url = url
        self.logo = logo
        self.event_id = event_id

    def __repr__(self):
        return '<Sponsor %r>' % (self.name)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'url': self.url,
                'logo': self.logo}
