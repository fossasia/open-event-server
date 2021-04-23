from app.models import db


class VideoRecording(db.Model):
    "Video Recording"

    __tablename__ = 'video_recordings'
    id = db.Column(db.Integer, primary_key=True)
    bbb_record_id = db.Column(db.String, nullable=True)
    participants = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String, nullable=False)
    start_time = db.Column(db.DateTime(timezone=False), nullable=False)
    end_time = db.Column(db.DateTime(timezone=False), nullable=False)

    video_stream_id = db.Column(
        db.Integer, db.ForeignKey('video_streams.id', ondelete='CASCADE'), nullable=False
    )
    video_stream = db.relationship('VideoStream', backref='video_recordings')

    def __repr__(self):
        return f'<VideoRecording {self.video_stream.name!r} {self.url!r}>'
