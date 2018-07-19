import random
from datetime import datetime, timedelta

import pytz

from app.models import db
from app.models.base import SoftDeletionModel


def generate_hash():
    hash_ = random.getrandbits(128)
    return str(hash_)


class RoleInvite(SoftDeletionModel):
    __tablename__ = 'role_invites'

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String, nullable=False)
    role_name = db.Column(db.String, nullable=False)

    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship('Event', back_populates='role_invites')

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'))
    role = db.relationship("Role")

    hash = db.Column(db.String)
    created_at = db.Column(db.DateTime(timezone=True))
    status = db.Column(db.String, default="pending")

    def __init__(self, email=None, role_name=None, event_id=None, role_id=None, created_at=None,
                 status="pending", hash=None, deleted_at=None):
        self.email = email
        self.role_name = role_name
        self.event_id = event_id
        self.role_id = role_id
        self.created_at = created_at
        self.status = status
        self.hash = generate_hash()
        self.deleted_at = deleted_at

    def has_expired(self):
        # Check if invitation link has expired (it expires after 24 hours)
        return datetime.now(pytz.utc) > self.created_at + timedelta(hours=24)

    def __repr__(self):
        return '<RoleInvite %r:%r:%r>' % (self.email,
                                          self.event_id,
                                          self.role_id,)

    def __str__(self):
        return self.__repr__()
