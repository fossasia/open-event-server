"""Copyright 2015 Rafal Kowalski"""
from . import db


class SponsorType(db.Model):
    """Sponsor Type"""
    __tablename__ = 'sponsor_type'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    event_id = db.Column(
        db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))

    def __init__(self, name=None, sponsor_id=None, event_id=None):
        self.name = name
        self.sponsor_id = sponsor_id
        self.event_id = event_id

    def __repr__(self):
        return '<SponsorType %r>' % self.name

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.name

    @property
    def serialize(self):
        return {'id': self.id, 'name': self.name}


class Sponsor(db.Model):
    """Sponsor model class"""
    __tablename__ = 'sponsors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    url = db.Column(db.String)
    level = db.Column(db.String)
    logo = db.Column(db.String)
    event_id = db.Column(
        db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    sponsor_type_id = db.Column(
        db.Integer, db.ForeignKey('sponsor_type.id', ondelete='CASCADE'))
    sponsor_type = db.relationship('SponsorType')

    def __init__(self, name=None, url=None, logo=None, event_id=None,
                 description=None, sponsor_type_id=None, level=None, ):
        self.name = name
        self.url = url
        self.logo = logo
        self.event_id = event_id
        self.level = level
        self.sponsor_type_id = sponsor_type_id
        self.description = description

    def __repr__(self):
        return '<Sponsor %r>' % self.name

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
            'url': self.url,
            'logo': self.logo
        }
