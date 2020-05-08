import uuid

from app.api.helpers.db import get_count
from app.models import db
from app.models.base import SoftDeletionModel


def get_new_slug(name):
    slug = (
        name.lower()
        .replace("& ", "")
        .replace(",", "")
        .replace("/", "-")
        .replace(" ", "-")
    )
    count = get_count(EventTopic.query.filter_by(slug=slug))
    if count == 0:
        return slug
    else:
        return '{}-{}'.format(slug, uuid.uuid4().hex)


class EventTopic(SoftDeletionModel):
    """Event topic object table"""

    __tablename__ = 'event_topics'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=True)
    system_image_url = db.Column(db.String)
    slug = db.Column(db.String, unique=True, nullable=False)
    events = db.relationship('Event', backref='event_topics')
    event_sub_topics = db.relationship('EventSubTopic', backref='event-topic')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.slug = get_new_slug(name=self.name)

    def __repr__(self):
        return '<EventTopic %r>' % self.name
