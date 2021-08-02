from app.api.helpers.db import get_new_slug
from app.models import db


class EventLocation(db.Model):
    """Event location object table"""

    __tablename__ = 'event_locations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    slug = db.Column(db.String, unique=True, nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.slug = get_new_slug(EventLocation, self.name)

    def __repr__(self):
        return '<EventLocation %r>' % self.slug
