import binascii
import os

from app.api.helpers.db import get_count
from app.models import db
from app.models.base import SoftDeletionModel


class SocialLink(SoftDeletionModel):
    __tablename__ = "social_links"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    link = db.Column(db.String, nullable=False)
    identifier = db.Column(db.String)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship("Event", backref="social_link")

    def __init__(self, **kwargs):
        super(SocialLink, self).__init__(**kwargs)
        self.identifier = self.get_new_identifier()

    def __repr__(self):
        return '<SocialLink %r>' % self.name
