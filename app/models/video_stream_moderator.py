from app.models import db
from app.models.base import SoftDeletionModel


class VideoStreamModerator(SoftDeletionModel):
    __tablename__ = 'video_stream_moderators'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False
    )
    video_stream_id = db.Column(
        db.Integer, db.ForeignKey('video_streams.id', ondelete='CASCADE'), nullable=False
    )
    user = db.relationship("User")
    video_stream = db.relationship("VideoStream", backref="moderators")

    def __repr__(self):
        return f'<UER {self.user!r}:{self.event_id!r}>'
