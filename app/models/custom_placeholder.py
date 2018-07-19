from sqlalchemy.orm import backref

from app.models import db


# ensures that if the image resizing fails somehow, respective image fields do not
def image_default(context):
    return context.current_parameters.get('original_image_url')


class CustomPlaceholder(db.Model):
    """email notifications model class"""
    __tablename__ = 'custom_placeholders'
    id = db.Column(db.Integer,
                   primary_key=True)
    name = db.Column(db.String)
    original_image_url = db.Column(db.String, nullable=False)
    thumbnail_image_url = db.Column(db.String, nullable=False, default=image_default)
    large_image_url = db.Column(db.String, nullable=False, default=image_default)
    icon_image_url = db.Column(db.String, nullable=False, default=image_default)
    copyright = db.Column(db.String)
    origin = db.Column(db.String)
    event_sub_topic_id = db.Column(db.Integer, db.ForeignKey('event_sub_topics.id', ondelete='CASCADE'))
    event_sub_topic = db.relationship('EventSubTopic', backref=backref('custom_placeholder', uselist=False))

    def __init__(self,
                 name=None,
                 original_image_url=None,
                 thumbnail_image_url=None,
                 large_image_url=None,
                 icon_image_url=None,
                 copyright=None,
                 origin=None,
                 event_sub_topic_id=None):
        self.name = name
        self.original_image_url = original_image_url
        self.thumbnail_image_url = thumbnail_image_url
        self.large_image_url = large_image_url
        self.icon_image_url = icon_image_url
        self.copyright = copyright
        self.origin = origin
        self.event_sub_topic_id = event_sub_topic_id

    def __str__(self):
        return 'Name: ' + self.name

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'thumbnail': self.thumbnail,
            'copyright': self.copyright,
            'origin': self.origin
        }
