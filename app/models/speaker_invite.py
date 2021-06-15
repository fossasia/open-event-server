import random

from sqlalchemy.schema import UniqueConstraint

from app.api.helpers.errors import ForbiddenError
from app.api.helpers.mail import send_email_speaker_invite
from app.api.helpers.permission_manager import has_access
from app.models import db
from app.models.helpers.timestamp import Timestamp
from app.models.session import Session
from app.settings import get_settings


def generate_token():
    hash_ = random.getrandbits(128)
    return str(hash_)


class SpeakerInvite(db.Model, Timestamp):
    __tablename__ = 'speaker_invites'
    __table_args__ = (
        UniqueConstraint(
            'email',
            'session_id',
            'event_id',
            name='email_session_event_uc',
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String, nullable=False)

    session_id = db.Column(
        db.Integer, db.ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False
    )
    session = db.relationship('Session', backref='speaker_invites')

    speaker_id = db.Column(db.Integer, db.ForeignKey('speaker.id', ondelete='CASCADE'))
    speaker = db.relationship('Speaker', backref='speaker_invites')

    event_id = db.Column(
        db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False
    )
    event = db.relationship('Event', backref='speaker_invites')

    token = db.Column(db.String, default=generate_token)
    status = db.Column(db.String, default="pending")

    def send_invite(self, inviter_email):
        """
        Send mail to invitee
        """
        session = Session.query.filter_by(id=self.session_id).first()
        frontend_url = get_settings()['frontend_url']
        link = f"{frontend_url}/speaker-invites?token={self.token}"
        if not has_access('is_speaker_for_session', id=session.id):
            raise ForbiddenError({'source': ''}, "Speaker Access Required")

        send_email_speaker_invite(self.email, session, link, inviter_email)
        # if user:
        #     notify_speaker_invitation(self, user, current_user)

    def __repr__(self):
        return f'<SpeakerInvite {self.email!r}:{self.session_id!r}>'
