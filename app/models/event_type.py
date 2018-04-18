import uuid

from app.api.helpers.db import get_count
from app.models import db


def get_new_slug(name):
    slug = name.lower().replace("& ", "").replace(",", "").replace("/", "-").replace(" ", "-")
    count = get_count(EventType.query.filter_by(slug=slug))
    if count == 0:
        return slug
    else:
        return '{}-{}'.format(slug, uuid.uuid4().hex)


class EventType(db.Model):
    """Event type object table"""

    __tablename__ = 'event_types'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    slug = db.Column(db.String, unique=True, nullable=False)
    events = db.relationship('Event', backref='event-type')

    def __init__(self,
                 name=None,
                 slug=None):

        self.name = name
        self.slug = get_new_slug(name=self.name)

    def __repr__(self):
        return '<EventType %r>' % self.name

    def __str__(self):
        return self.__repr__()

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {'id': self.id, 'name': self.name, 'slug': self.slug}
