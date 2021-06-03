import random
from datetime import datetime, timedelta

import pytz
from flask_jwt_extended import current_user
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.sql import func

from app.api.helpers.errors import ForbiddenError
from app.api.helpers.mail import send_email_role_invite
from app.api.helpers.notification import notify_event_role_invitation
from app.api.helpers.permission_manager import has_access
from app.models import db
from app.models.event import Event
from app.models.user import User
from app.settings import get_settings


def generate_hash():
    hash_ = random.getrandbits(128)
    return str(hash_)


class RoleInvite(db.Model):
    __tablename__ = 'role_invites'
    __table_args__ = (
        UniqueConstraint(
            'email',
            'role_id',
            'event_id',
            name='email_role_event_uc',
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String, nullable=False)
    role_name = db.Column(db.String, nullable=False)

    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship('Event', back_populates='role_invites')

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'))
    role = db.relationship("Role")

    hash = db.Column(db.String, default=generate_hash)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    status = db.Column(db.String, default="pending")

    def has_expired(self):
        # Check if invitation link has expired (it expires after 24 hours)
        return datetime.now(pytz.utc) > self.created_at + timedelta(hours=24)

    def send_invite(self):
        """
        Send mail to invitee
        """
        user = User.query.filter_by(email=self.email).first()
        event = Event.query.filter_by(id=self.event_id).first()
        frontend_url = get_settings()['frontend_url']
        link = f"{frontend_url}/role-invites?token={self.hash}"
        if not has_access('is_coorganizer', event_id=event.id):
            raise ForbiddenError({'source': ''}, "Co-Organizer Access Required")

        send_email_role_invite(self.email, self.role_name, event.name, link)
        if user:
            notify_event_role_invitation(self, user, current_user)

    def __repr__(self):
        return '<RoleInvite {!r}:{!r}:{!r}>'.format(
            self.email, self.event_id, self.role_id
        )
