from app.models import db
from app.models.base import SoftDeletionModel


class SessionsSpeakersLink(SoftDeletionModel):
    __tablename__ = 'sessions_speakers_links'

    id = db.Column(db.Integer, primary_key=True)

    event_id = db.Column(db.Integer, nullable=False)
    session_id = db.Column(db.Integer, nullable=False)
    speaker_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<SSLink {self.session_id!r}:{self.speaker_id!r}>'
