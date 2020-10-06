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
    return get_new_social_link_identifier(length)


class SocialLink(SoftDeletionModel):
    __tablename__ = "social_links"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    link = db.Column(db.String, nullable=False)
    identifier = db.Column(db.String, default=get_new_social_link_identifier)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship("Event", backref="social_link")

    def __repr__(self):
        return '<SocialLink %r>' % self.name
