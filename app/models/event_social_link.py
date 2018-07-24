from future.utils import python_2_unicode_compatible
from sqlalchemy.dialects.postgresql import UUID

from app.models import db


@python_2_unicode_compatible
class EventSocialLink(db.Model):
    """Event Social Link object table"""
    __tablename__ = 'event_social_link'
    __table_args__ = (db.UniqueConstraint('social_link_id', 'event_id', name='unique_event_social_link'),)

    social_link_id = db.Column(UUID, db.ForeignKey('social_links.id', ondelete='CASCADE'), nullable=False)
    event_id = db.Column(UUID, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    event = db.relationship('Event',
                            backref='event_social_link',
                            foreign_keys=[event_id])
    social_link = db.relationship('SocialLink',
                                  backref='event_social_link',
                                  foreign_keys=[social_link_id])
    value = db.Column(db.String, nullable=False)

    def __init__(self,
                 social_link_id=None,
                 event_id=None,
                 value=None):
        self.social_link_id = social_link_id
        self.event_id = event_id
        self.value = value
