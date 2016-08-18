"""Copyright 2015 Rafal Kowalski"""
from . import db


class CustomPlaceholder(db.Model):
    """email notifications model class"""
    __tablename__ = 'custom_placeholder'
    id = db.Column(db.Integer,
                   primary_key=True)
    name = db.Column(db.String)
    url = db.Column(db.String)
    thumbnail = db.Column(db.String)

    def __init__(self,
                 name=None,
                 url=None,
                 thumbnail=None):
        self.name = name
        self.url = url
        self.thumbnail = thumbnail

    def __str__(self):
        return 'Name:' + unicode(self.name).encode('utf-8')

    def __unicode__(self):
        return unicode(self.id)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'thumbnail': self.thumbnail
        }
