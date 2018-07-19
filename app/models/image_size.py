from app.models import db


class ImageSizes(db.Model):
    """image size model class"""
    __tablename__ = 'image_sizes'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String)
    full_width = db.Column(db.Integer)
    full_height = db.Column(db.Integer)
    full_aspect = db.Column(db.Boolean, default=False)
    full_quality = db.Column(db.Integer)
    icon_width = db.Column(db.Integer)
    icon_height = db.Column(db.Integer)
    icon_aspect = db.Column(db.Boolean, default=False)
    icon_quality = db.Column(db.Integer)
    thumbnail_width = db.Column(db.Integer)
    thumbnail_height = db.Column(db.Integer)
    thumbnail_aspect = db.Column(db.Boolean, default=False)
    thumbnail_quality = db.Column(db.Integer)
    logo_width = db.Column(db.Integer)
    logo_height = db.Column(db.Integer)
    small_size_width_height = db.Column(db.Integer)
    small_size_quality = db.Column(db.Integer)
    thumbnail_size_width_height = db.Column(db.Integer)
    thumbnail_size_quality = db.Column(db.Integer)
    icon_size_width_height = db.Column(db.Integer)
    icon_size_quality = db.Column(db.Integer)

    def __init__(self,
                 type=None,
                 full_width=None,
                 full_height=None,
                 full_aspect=False,
                 full_quality=None,
                 icon_width=None,
                 icon_height=None,
                 icon_aspect=False,
                 icon_quality=None,
                 thumbnail_width=None,
                 thumbnail_height=None,
                 thumbnail_aspect=False,
                 thumbnail_quality=None,
                 logo_width=None,
                 logo_height=None,
                 small_size_width_height=None,
                 small_size_quality=None,
                 thumbnail_size_width_height=None,
                 thumbnail_size_quality=None,
                 icon_size_width_height=None,
                 icon_size_quality=None):
        self.type = type
        self.full_width = full_width
        self.full_height = full_height
        self.full_aspect = full_aspect
        self.full_quality = full_quality
        self.icon_width = icon_width
        self.icon_height = icon_height
        self.icon_aspect = icon_aspect
        self.icon_quality = icon_quality
        self.thumbnail_width = thumbnail_width
        self.thumbnail_height = thumbnail_height
        self.thumbnail_aspect = thumbnail_aspect
        self.thumbnail_quality = thumbnail_quality
        self.logo_width = logo_width
        self.logo_height = logo_height
        self.small_size_width_height = small_size_width_height
        self.small_size_quality = small_size_quality
        self.thumbnail_size_width_height = thumbnail_size_width_height
        self.thumbnail_size_quality = thumbnail_size_quality
        self.icon_size_width_height = icon_size_width_height
        self.icon_size_quality = icon_size_quality

    def __str__(self):
        return 'Image Size: ' + self.id

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'type': self.type,
            'full_width': self.full_width,
            'full_height': self.full_height,
            'full_aspect': self.full_aspect,
            'full_quality': self.full_quality,
            'icon_width': self.icon_width,
            'icon_height': self.icon_height,
            'icon_aspect': self.icon_aspect,
            'icon_quality': self.icon_quality,
            'thumbnail_width': self.thumbnail_width,
            'thumbnail_height': self.thumbnail_height,
            'thumbnail_aspect': self.thumbnail_aspect,
            'thumbnail_quality': self.thumbnail_quality,
            'logo_height': self.logo_height,
            'logo_width': self.logo_width,
            'small_size_width_height': self.small_size_width_height,
            'small_size_quality': self.small_size_quality,
            'thumbnail_size_width_height': self.thumbnail_size_width_height,
            'thumbnail_size_quality': self.thumbnail_size_quality,
            'icon_size_width_height': self.icon_size_width_height,
            'icon_size_quality': self.icon_size_quality
        }
