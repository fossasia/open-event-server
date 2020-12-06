from flask_jwt_extended import current_user
from sqlalchemy import or_
from sqlalchemy.orm import backref

from app.api.helpers.permission_manager import has_access
from app.models import db
from app.models.order import Order
from app.models.ticket_holder import TicketHolder


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

    event_id = db.Column(
        db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), unique=True
    )
    event = db.relationship('Event', backref=backref('video_stream', uselist=False))

    def __repr__(self):
        return f'<VideoStream {self.name!r} {self.url!r}>'

    @property
    def event(self):
        return self.rooms[0].event

    @property
    def user_can_access(self):
        rooms = self.rooms
        if not rooms:
            return False
        event_id = rooms[0].event_id
        user = current_user
        if user.is_staff or has_access('is_coorganizer', event_id=event_id):
            return True
        return db.session.query(
            TicketHolder.query.filter_by(event_id=event_id, user=user)
            .join(Order)
            .filter(or_(Order.status == 'completed', Order.status == 'placed'))
            .exists()
        ).scalar()
