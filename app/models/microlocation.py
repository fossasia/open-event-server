import re

from app.models import db
from app.models.base import SoftDeletionModel


class Microlocation(SoftDeletionModel):
    """Microlocation model class"""

    __tablename__ = 'microlocations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    floor = db.Column(db.Integer)
    hidden_in_scheduler = db.Column(db.Boolean, default=False, nullable=False)
    position = db.Column(db.Integer, default=0, nullable=False)
    room = db.Column(db.String)
    is_chat_enabled = db.Column(db.Boolean, default=False, nullable=True)
    is_global_event_room = db.Column(db.Boolean, default=False, nullable=True)
    chat_room_id = db.Column(db.String, nullable=True)
    session = db.relationship('Session', backref="microlocation")
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    video_stream_id = db.Column(
        db.Integer, db.ForeignKey('video_streams.id', ondelete='CASCADE')
    )

    @staticmethod
    def get_service_name():
        return 'microlocation'

    def __repr__(self):
        return '<Microlocation %r>' % self.name

    @property
    def safe_video_stream(self):
        """Conditionally return video stream after applying access control"""
        stream = self.video_stream
        if stream and stream.user_can_access:
            return stream
        return None

    @safe_video_stream.setter
    def safe_video_stream(self, value):
        self.video_stream = value

    @property
    def chat_room_name(self):
        return re.sub('[^0-9a-zA-Z!]', '-', self.name) + '-' + str(self.id)
