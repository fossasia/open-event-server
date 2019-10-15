import uuid

from dataclasses import dataclass
from app.api.helpers.db import get_count
from app.models import db


def get_new_slug(name):
    slug = name.lower().replace("& ", "").replace(",", "").replace("/", "-").replace(" ", "-")
    count = get_count(EventLocation.query.filter_by(slug=slug))
    if count == 0:
        return slug
    else:
        return '{}-{}'.format(slug, uuid.uuid4().hex)


@dataclass(init=True, repr=True, unsafe_hash=True)
class EventLocation(db.Model):
    """Event location object table"""

    __tablename__ = 'event_locations'

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name: str = db.Column(db.String, nullable=False)
    slug: str = db.Column(db.String, unique=True, nullable=False)
