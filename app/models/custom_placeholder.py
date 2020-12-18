from sqlalchemy.orm import backref

from app.models import db


# ensures that if the image resizing fails somehow, respective image fields do not
def image_default(context):
    return context.current_parameters.get('original_image_url')


class CustomPlaceholder(db.Model):
    """email notifications model class"""

    __tablename__ = 'custom_placeholders'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    original_image_url = db.Column(db.String, nullable=False)
    thumbnail_image_url = db.Column(db.String, nullable=False, default=image_default)
    large_image_url = db.Column(db.String, nullable=False, default=image_default)
    icon_image_url = db.Column(db.String, nullable=False, default=image_default)
    copyright = db.Column(db.String)
    origin = db.Column(db.String)
    event_sub_topic_id = db.Column(
        db.Integer, db.ForeignKey('event_sub_topics.id', ondelete='CASCADE')
    )
    event_sub_topic = db.relationship(
        'EventSubTopic', backref=backref('custom_placeholder', uselist=False)
    )

    def __repr__(self):
        return 'Name: ' + self.name
