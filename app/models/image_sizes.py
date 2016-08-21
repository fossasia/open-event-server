"""Copyright 2015 Rafal Kowalski"""
from . import db


class ImageSizes(db.Model):
    """image size model class"""
    __tablename__ = 'image_sizes'
    id = db.Column(db.Integer,
                   primary_key=True)
    full_width = db.Column(db.Integer)
    full_height = db.Column(db.Integer)
    icon_width = db.Column(db.Integer)
    icon_height = db.Column(db.Integer)
    thumbnail_width = db.Column(db.Integer)
    thumbnail_height = db.Column(db.Integer)

    def __init__(self,
                 full_width=None,
                 full_height=None,
                 icon_width=None,
                 icon_height=None,
                 thumbnail_width=None,
                 thumbnail_height=None):
        self.full_width = full_width
        self.full_height = full_height
        self.icon_width = icon_width
        self.icon_height = icon_height
        self.thumbnail_width = thumbnail_width
        self.thumbnail_height = thumbnail_height

    def __str__(self):
        return 'Page:' + unicode(self.page).encode('utf-8')

    def __unicode__(self):
        return unicode(self.id)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'full_width': self.full_width,
            'full_height': self.full_height,
            'icon_width': self.icon_width,
            'icon_height': self.icon_height,
            'thumbnail_width': self.thumbnail_width,
            'thumbnail_height': self.thumbnail_height
        }
