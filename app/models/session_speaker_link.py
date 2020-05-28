from app.models import db
from app.models.base import SoftDeletionModel


class SessionsSpeakersLink(SoftDeletionModel):
    __tablename__ = 'sessions_speakers_links'

    id = db.Column(db.Integer, primary_key=True)

    event_id = db.Column(db.Integer)
    session_id = db.Column(db.Integer)
    speaker_id = db.Column(db.Integer)
    session_state = db.Column(db.String, nullable=False)

    def __repr__(self):
        return '<SSLink %r:%r:%r>' % (
            self.session_id,
            self.speaker_id,
            self.session_state,
        )
