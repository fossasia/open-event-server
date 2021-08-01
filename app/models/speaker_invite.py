from app.api.helpers.errors import ForbiddenError
from app.api.helpers.mail import send_email_speaker_invite
from app.api.helpers.permission_manager import has_access
from app.models import db
from app.models.helpers.timestamp import Timestamp
from app.models.session import Session
from app.models.speaker import Speaker
from app.settings import get_settings


class SpeakerInvite(db.Model, Timestamp):
    __tablename__ = 'speaker_invites'

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String, nullable=False)

    status = db.Column(db.String, default="pending")

    session_id = db.Column(
        db.Integer, db.ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False
    )
    session = db.relationship('Session', backref='speaker_invites')

    event_id = db.Column(
        db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False
    )
    event = db.relationship('Event', backref='speaker_invites')

    def send_invite(self, inviter_email):
        """
        Send mail to invitee
        """
        session = Session.query.filter_by(id=self.session_id).first()
        frontend_url = get_settings()['frontend_url']
        cfs_link = f"{frontend_url}/e/{self.event.identifier}/cfs"
        if not has_access('is_speaker_for_session', id=session.id):
            raise ForbiddenError({'source': ''}, "Speaker Access Required")
        inviter = Speaker.query.filter_by(
            email=inviter_email, event_id=session.event_id, deleted_at=None
        ).first()
        send_email_speaker_invite(self.email, session, cfs_link, inviter)

    def __repr__(self):
        return f'<SpeakerInvite {self.email!r}:{self.session_id!r}>'
