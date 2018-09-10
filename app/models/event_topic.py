import uuid
from flask import current_app as app, request
import urllib.parse

from app.api.helpers.db import get_count
from app.models import db
from app.models.base import SoftDeletionModel


def get_new_slug(name):
    slug = name.lower().replace("& ", "").replace(",", "").replace("/", "-").replace(" ", "-")
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

    def __init__(self,
                 name=None,
                 system_image_url=None,
                 slug=None,
                 deleted_at=None):

        self.name = name
        self.system_image_url = system_image_url
        self.slug = get_new_slug(name=self.name)
        self.deleted_at = deleted_at

    def __repr__(self):
        return '<EventTopic %r>' % self.name

    def __str__(self):
        return self.__repr__()

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {'id': self.id, 'name': self.name, 'slug': self.slug}
