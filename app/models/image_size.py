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

    def __repr__(self):
        return 'Image Size: ' + self.id
