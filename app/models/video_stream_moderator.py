from citext import CIText
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy_utils.models import generic_repr

from app.models import db


@generic_repr
class VideoStreamModerator(db.Model):
    __tablename__ = 'video_stream_moderators'
    __table_args__ = (
        UniqueConstraint(
            'email', 'video_stream_id', name='uq_user_email_video_stream_moderator'
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(CIText, nullable=False)
    video_stream_id = db.Column(
        db.Integer, db.ForeignKey('video_streams.id', ondelete='CASCADE'), nullable=False
    )
    user = db.relationship(
        'User',
        foreign_keys=[email],
        primaryjoin='User.email == VideoStreamModerator.email',
        viewonly=True,
        sync_backref=False,
    )
    video_stream = db.relationship("VideoStream", backref="moderators")
