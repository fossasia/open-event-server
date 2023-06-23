from sqlalchemy_utils import generic_repr

from app.models import db
from app.models.helpers.timestamp import Timestamp
from app.models.helpers.versioning import clean_html, clean_up_string

exhibitors_sessions = db.Table(
    'exhibitors_sessions',
    db.Column('session_id', db.Integer, db.ForeignKey('sessions.id', ondelete='CASCADE')),
    db.Column(
        'exhibitor_id', db.Integer, db.ForeignKey('exhibitors.id', ondelete='CASCADE')
    ),
    db.PrimaryKeyConstraint('session_id', 'exhibitor_id'),
)


@generic_repr
class Exhibitor(db.Model, Timestamp):
    class Status:
        PENDING = 'pending'
        ACCEPTED = 'accepted'

        STATUSES = [PENDING, ACCEPTED]

    __tablename__ = 'exhibitors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    status = db.Column(
        db.String, nullable=False, default=Status.PENDING, server_default=Status.PENDING
    )
    description = db.Column(db.String)
    url = db.Column(db.String)
    position = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    logo_url = db.Column(db.String)
    banner_url = db.Column(db.String)
    thumbnail_image_url = db.Column(db.String)
    video_url = db.Column(db.String)
    slides_url = db.Column(db.String)
    contact_email = db.Column(db.String)
    contact_link = db.Column(db.String)
    enable_video_room = db.Column(
        db.Boolean, default=False, nullable=False, server_default='False'
    )
    social_links = db.Column(db.JSON)
    event_id = db.Column(
        db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False
    )
    sessions = db.relationship(
        'Session',
        secondary=exhibitors_sessions,
        backref=db.backref('exhibitors', lazy='dynamic'),
    )

    def __setattr__(self, name, value):
        if name == 'description':
            super().__setattr__(name, clean_html(clean_up_string(value)))
        else:
            super().__setattr__(name, value)
