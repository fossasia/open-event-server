"""Copyright 2015 Rafal Kowalski"""
from . import db


class ImageSizes(db.Model):
    """image size model class"""
    __tablename__ = 'image_sizes'
    id = db.Column(db.Integer,
                   primary_key=True)
    type = db.Column(db.String)
    full_width = db.Column(db.Integer)
    full_height = db.Column(db.Integer)
    full_aspect = db.Column(db.String)
    icon_width = db.Column(db.Integer)
    icon_height = db.Column(db.Integer)
    icon_aspect = db.Column(db.String)
    thumbnail_width = db.Column(db.Integer)
    thumbnail_height = db.Column(db.Integer)
    thumbnail_aspect = db.Column(db.String)
    logo_width = db.Column(db.Integer)
    logo_height = db.Column(db.Integer)

    def __init__(self,
                 type=None,
                 full_width=None,
                 full_height=None,
                 full_aspect=None,
                 icon_width=None,
                 icon_height=None,
                 icon_aspect=None,
                 thumbnail_width=None,
                 thumbnail_height=None,
                 thumbnail_aspect=None,
                 logo_width=None,
                 logo_height=None):
        self.type = type
        self.full_width = full_width
        self.full_height = full_height
        self.full_aspect = full_aspect
        self.icon_width = icon_width
        self.icon_height = icon_height
        self.icon_aspect = icon_aspect
        self.thumbnail_width = thumbnail_width
        self.thumbnail_height = thumbnail_height
        self.thumbnail_aspect = thumbnail_aspect
        self.logo_width = logo_width
        self.logo_height = logo_height

    def __str__(self):
        return 'Page:' + unicode(self.page).encode('utf-8')

    def __unicode__(self):
        return unicode(self.id)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'type': self.type,
            'full_width': self.full_width,
            'full_height': self.full_height,
            'full_aspect': self.full_aspect,
            'icon_width': self.icon_width,
            'icon_height': self.icon_height,
            'icon_aspect': self.icon_aspect,
            'thumbnail_width': self.thumbnail_width,
            'thumbnail_height': self.thumbnail_height,
            'thumbnail_aspect': self.thumbnail_aspect
        }
