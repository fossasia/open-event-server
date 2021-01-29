from app.models import db
from app.models.helpers.timestamp import Timestamp


class VideoChannel(db.Model, Timestamp):
    "Video Channel like Jitsi, BBB, etc"

    __tablename__ = 'video_channels'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)  # eg. Jitsi Meet
    provider = db.Column(db.String, nullable=False)  # eg. jitsi, bbb, youtube
    url = db.Column(db.String, nullable=False)  # Public URL eg. https://meet.jit.si
    api_url = db.Column(db.String)  # eg. https://api.jitsi.net
    api_key = db.Column(db.String)
    # Extra info stored for server if needed for integration like settings
    extra = db.Column(db.JSON)

    def __repr__(self) -> str:
        return f'<VideoChannel {self.id} {self.name} {self.provider} {self.url}>'
