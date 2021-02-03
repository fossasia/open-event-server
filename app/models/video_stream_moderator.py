from app.models import db
from app.models.base import SoftDeletionModel


class VideoStreamModerator(SoftDeletionModel):
    __tablename__ = 'video_stream_moderator'

    id = db.Column(db.Integer, primary_key=True)

    event_id = db.Column(
        db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False
    )

    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False
    )
    user = db.relationship("User")
    event = db.relationship("Event")

    def __repr__(self):
        return f'<UER {self.user!r}:{self.event_id!r}>'
