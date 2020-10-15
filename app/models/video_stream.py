from app.models import db


class VideoStream(db.Model):
    "Video Stream or Room"

    __tablename__ = 'video_streams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    # URL for stream or meeting like YouTube or Jitsi
    url = db.Column(db.String, nullable=False)
    # Password for joining the meeting if controlled
    password = db.Column(db.String)
    # Any additional information for organizer or user
    additional_information = db.Column(db.String)

    # Rooms to which the stream is linked. A room can have
    # a single video stream linked. But a video stream can be
    # linked to several rooms
    rooms = db.relationship('Microlocation', backref='video_stream')

    def __repr__(self):
        return f'<VideoStream {self.name!r} {self.url!r}>'
