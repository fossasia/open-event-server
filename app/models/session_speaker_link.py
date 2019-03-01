from app.models import db
from app.models.base import SoftDeletionModel


class SessionsSpeakersLink(SoftDeletionModel):
    __tablename__ = 'sessions_speakers_links'

    id = db.Column(db.Integer, primary_key=True)

    event_id = db.Column(db.Integer)
    session_id = db.Column(db.Integer)
    speaker_id = db.Column(db.Integer)
    session_state = db.Column(db.String, nullable=False)

    def __init__(self,
                 session_id=None,
                 speaker_id=None,
                 event_id=None,
                 session_state=None,
                 deleted_at=None):

        self.session_id = session_id
        self.speaker_id = speaker_id
        self.event_id = event_id
        self.session_state = session_state
        self.deleted_at = deleted_at

    def __repr__(self):
        return '<SSLink %r:%r:%r>' % (self.session_id,
                                      self.speaker_id,
                                      self.session_state)

    def __str__(self):
        return self.__repr__()
