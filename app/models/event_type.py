from app.api.helpers.db import get_new_slug
from app.models import db
from app.models.base import SoftDeletionModel


class EventType(SoftDeletionModel):
    """Event type object table"""

    __tablename__ = 'event_types'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    slug = db.Column(db.String, unique=True, nullable=False)
    events = db.relationship('Event', backref='event-type')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.slug = get_new_slug(EventType, self.name)

    def __repr__(self):
        return '<EventType %r>' % self.name
