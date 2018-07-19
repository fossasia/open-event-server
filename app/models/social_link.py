import binascii
import os

from app.api.helpers.db import get_count
from app.models import db
from app.models.base import SoftDeletionModel


def get_new_social_link_identifier(length=8):
    """
    returns a new social link identifier.
    :param length:
    :return:
    """
    identifier = str(binascii.b2a_hex(os.urandom(int(length / 2))), 'utf-8')
    count = get_count(SocialLink.query.filter_by(identifier=identifier))
    if count == 0:
        return identifier
    else:
        return get_new_social_link_identifier(length)


class SocialLink(SoftDeletionModel):
    __tablename__ = "social_links"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    link = db.Column(db.String, nullable=False)
    identifier = db.Column(db.String)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship("Event", backref="social_link")

    def __init__(self, name=None, link=None, event_id=None, deleted_at=None, identifier=None):
        self.name = name
        self.link = link
        self.event_id = event_id
        self.deleted_at = deleted_at
        if identifier:
            self.identifier = identifier
        else:
            self.identifier = get_new_social_link_identifier()

    def __repr__(self):
        return '<SocialLink %r>' % self.name

    def __str__(self):
        return self.__repr__()

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {'id': self.id, 'name': self.name, 'link': self.link}
