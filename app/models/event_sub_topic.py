import uuid

from app.api.helpers.db import get_count
from app.models import db
from app.models.base import SoftDeletionModel


def get_new_slug(name):
    slug = name.lower().replace("& ", "").replace(",", "").replace("/", "-").replace(" ", "-")
    count = get_count(EventSubTopic.query.filter_by(slug=slug))
    if count == 0:
        return slug
    else:
        return '{}-{}'.format(slug, uuid.uuid4().hex)


class EventSubTopic(SoftDeletionModel):
    """Event sub topic object table"""

    __tablename__ = 'event_sub_topics'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    slug = db.Column(db.String, unique=True, nullable=False)
    events = db.relationship('Event', backref='event-sub-topic')
    event_topic = db.relationship('EventTopic', backref='event-sub-topics')
    event_topic_id = db.Column(db.Integer, db.ForeignKey('event_topics.id', ondelete='CASCADE'))

    def __init__(self,
                 name=None,
                 slug=None,
                 event_topic_id=None,
                 deleted_at=None):

        self.name = name
        self.slug = get_new_slug(name=self.name)
        self.event_topic_id = event_topic_id
        self.deleted_at = deleted_at

    def __repr__(self):
        return '<EventSubTopic %r>' % self.name

    def __str__(self):
        return self.__repr__()

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {'id': self.id, 'name': self.name, 'slug': self.slug, 'event_topic_id': self.event_topic_id}
