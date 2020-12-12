from sqlalchemy import func

from app.models import db


class VideoChannel(db.Model):
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

    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    modified_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )
