import uuid

from app.api.helpers.db import get_count
from app.models import db


def get_new_slug(name):
    slug = name.lower().replace("& ", "").replace(",", "").replace("/", "-").replace(" ", "-")
    count = get_count(EventLocation.query.filter_by(slug=slug))
    if count == 0:
        return slug
    else:
        return '{}-{}'.format(slug, uuid.uuid4().hex)


class EventLocation(db.Model):
    """Event location object table"""

    __tablename__ = 'event_locations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    slug = db.Column(db.String, unique=True, nullable=False)

    def __init__(self,
                 name=None,
                 slug=None):

        self.name = name
        self.slug = get_new_slug(name=self.name)

    def __repr__(self):
        return '<EventLocation %r>' % self.slug

    def __str__(self):
        return self.__repr__()
