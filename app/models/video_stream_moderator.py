from sqlalchemy.schema import UniqueConstraint

from app.models import db


class VideoStreamModerator(db.Model):
    __tablename__ = 'video_stream_moderators'
    __table_args__ = (
        UniqueConstraint('user_id', 'video_stream_id', name='user_video_stream_id'),
    )

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
        return f'{self.user!r}'
