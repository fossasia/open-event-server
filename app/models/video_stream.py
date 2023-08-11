import re

from flask_jwt_extended import current_user
from sqlalchemy import or_
from sqlalchemy.orm import backref

from app.api.helpers.permission_manager import has_access
from app.models import db
from app.models.order import Order
from app.models.session import Session
from app.models.speaker import Speaker
from app.models.ticket_holder import TicketHolder
from app.models.video_channel import VideoChannel


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
    bg_img_url = db.Column(db.String)
    # Extra info stored for server if needed for integration like settings
    extra = db.Column(db.JSON)

    # Rooms to which the stream is linked. A room can have
    # a single video stream linked. But a video stream can be
    # linked to several rooms
    rooms = db.relationship('Microlocation', backref='video_stream')

    event_id = db.Column(
        db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), unique=True
    )
    event = db.relationship('Event', backref=backref('video_stream', uselist=False))

    channel_id = db.Column(
        db.Integer, db.ForeignKey('video_channels.id', ondelete='CASCADE')
    )
    channel = db.relationship(VideoChannel, backref='streams')
    is_chat_enabled = db.Column(db.Boolean, default=False, nullable=True)
    is_global_event_room = db.Column(db.Boolean, default=False, nullable=True)
    chat_room_id = db.Column(db.String, nullable=True)

    def __repr__(self):
        return f'<VideoStream {self.name!r} {self.url!r}>'

    def user_is_speaker(self, event_id=None):
        query = (
            Speaker.query.filter(Speaker.email == current_user.email)
            .join(Speaker.sessions)
            .filter(
                or_(
                    Session.state == Session.State.CONFIRMED,
                    Session.state == Session.State.ACCEPTED,
                )
            )
        )
        event_id = event_id or self.event_id
        if event_id:
            query = query.filter(Session.event_id == event_id)
        elif self.rooms:
            room_ids = {room.id for room in self.rooms}
            query = query.filter(Session.microlocation_id.in_(room_ids))
        else:
            raise ValueError("Video Stream must have rooms or event")
        return db.session.query(query.exists()).scalar()

    @property
    def user_is_confirmed_speaker(self):
        if not current_user or not (self.event_id or self.rooms):
            return False
        return self.user_is_speaker()

    @property
    def _event_id(self):
        return self.event_id or self.rooms[0].event_id

    @property
    def user_is_moderator(self):
        if not current_user or not (self.event_id or self.rooms):
            return False
        user = current_user
        if user.is_staff or has_access('is_coorganizer', event_id=self._event_id):
            return True
        return user.email in list(map(lambda x: x.email, self.moderators))

    @property
    def user_can_access(self):
        if not current_user or not (self.event_id or self.rooms):
            return False
        return (
            self.user_is_moderator
            or self.user_is_speaker(self._event_id)
            or db.session.query(
                TicketHolder.query.filter_by(event_id=self._event_id, user=current_user)
                .join(Order)
                .filter(or_(Order.status == 'completed', Order.status == 'placed'))
                .exists()
            ).scalar()
        )

    @property
    def chat_room_name(self):
        return re.sub('[^0-9a-zA-Z!]', '-', self.name) + '-' + str(self.id)
