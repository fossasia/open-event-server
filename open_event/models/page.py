"""Copyright 2016 Rafal Kowalski"""
from . import db


class Page(db.Model):
    """Page model class"""
    __tablename__ = 'pages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    title = db.Column(db.String)
    url = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    place = db.Column(db.String)
    index = db.Column(db.Integer)
    def __init__(self, name=None,title=None, description=None, url=None, place=None):
        self.name = name
        self.description = description
        self.title = title
        self.url = url
        self.place = place

    def __repr__(self):
        return '<Page %r>' % self.name

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
            'description': self.description,
            'title': self.title,
            'url': self.url,
            'place': self.place
        }
