from sqlalchemy.orm import backref

from app.models import db
from app.models.video_channel import VideoChannel


class TranslationChannel(db.Model):
    """Translation Channel"""

    __tablename__ = "translation_channels"
    id = db.Column(db.Integer, primary_key=True)
    video_stream_id = db.Column(
        db.Integer, db.ForeignKey('video_streams.id', ondelete='CASCADE')
    )
    video_stream = db.relationship('VideoStream', backref=backref('video_stream'))

    channel_id = db.Column(
        db.Integer, db.ForeignKey('video_channels.id', ondelete='CASCADE')
    )
    channel = db.relationship(VideoChannel, backref='stream_channels')
    name = db.Column(db.String)
    url = db.Column(db.String)
