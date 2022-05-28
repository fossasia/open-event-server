import datetime

import pytz
from flask_jwt_extended import current_user
from sqlalchemy import event, func
from sqlalchemy.sql import func as sql_func
from sqlalchemy_utils import aggregated

from app.models import db
from app.models.base import SoftDeletionModel
from app.models.feedback import Feedback
from app.models.helpers.versioning import clean_html, clean_up_string
from app.models.user_favourite_session import UserFavouriteSession

speakers_sessions = db.Table(
    'speakers_sessions',
    db.Column('speaker_id', db.Integer, db.ForeignKey('speaker.id', ondelete='CASCADE')),
    db.Column('session_id', db.Integer, db.ForeignKey('sessions.id', ondelete='CASCADE')),
    db.PrimaryKeyConstraint('speaker_id', 'session_id'),
)


class Session(SoftDeletionModel):
    """Session model class"""

    class State:
        PENDING = 'pending'
        ACCEPTED = 'accepted'
        CONFIRMED = 'confirmed'
        REJECTED = 'rejected'

    __tablename__ = 'sessions'
    __table_args__ = (
        db.Index('session_event_idx', 'event_id'),
        db.Index('session_state_idx', 'state'),
    )
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    subtitle = db.Column(db.String)
    website = db.Column(db.String)
    twitter = db.Column(db.String)
    facebook = db.Column(db.String)
    github = db.Column(db.String)
    linkedin = db.Column(db.String)
    instagram = db.Column(db.String)
    gitlab = db.Column(db.String)
    mastodon = db.Column(db.String)
    short_abstract = db.Column(db.Text, default='')
    long_abstract = db.Column(db.Text, default='')
    comments = db.Column(db.Text)
    language = db.Column(db.String)
    level = db.Column(db.String)
    starts_at = db.Column(db.DateTime(timezone=True))
    ends_at = db.Column(db.DateTime(timezone=True))
    track_id = db.Column(db.Integer, db.ForeignKey('tracks.id', ondelete='CASCADE'))
    microlocation_id = db.Column(
        db.Integer, db.ForeignKey('microlocations.id', ondelete='CASCADE')
    )
    session_type_id = db.Column(
        db.Integer, db.ForeignKey('session_types.id', ondelete='CASCADE')
    )
    speakers = db.relationship(
        'Speaker',
        secondary=speakers_sessions,
        backref=db.backref('sessions', lazy='dynamic'),
    )

    feedbacks = db.relationship('Feedback', backref="session")
    slides_url = db.Column(db.String)
    slides = db.Column(db.JSON)
    video_url = db.Column(db.String)
    audio_url = db.Column(db.String)
    signup_url = db.Column(db.String)

    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    creator = db.relationship('User')
    state = db.Column(db.String, default="pending")
    created_at = db.Column(db.DateTime(timezone=True), default=sql_func.now())
    submitted_at = db.Column(db.DateTime(timezone=True))
    submission_modifier = db.Column(db.String)
    is_mail_sent = db.Column(db.Boolean, default=False)
    last_modified_at = db.Column(db.DateTime(timezone=True), default=func.now())
    send_email = db.Column(db.Boolean, nullable=True)
    is_locked = db.Column(db.Boolean, default=False, nullable=False)
    complex_field_values = db.Column(db.JSON)

    @staticmethod
    def get_service_name():
        return 'session'

    @property
    def is_accepted(self):
        return self.state == "accepted"

    @property
    def organizer_site_link(self):
        return self.event.organizer_site_link + f"/session/{self.id}"

    @aggregated(
        'feedbacks', db.Column(db.Float, default=0, server_default='0', nullable=False)
    )
    def average_rating(self):
        return func.coalesce(func.avg(Feedback.rating), 0)

    @aggregated(
        'feedbacks', db.Column(db.Integer, default=0, server_default='0', nullable=False)
    )
    def rating_count(self):
        return func.count('1')

    @aggregated(
        'favourites', db.Column(db.Integer, default=0, server_default='0', nullable=False)
    )
    def favourite_count(self):
        return func.count('1')

    @property
    def favourite(self):
        if not current_user:
            return None
        return UserFavouriteSession.query.filter_by(
            user=current_user, session=self
        ).first()

    @property
    def site_link(self):
        return self.event.site_link + f"/session/{self.id}"

    @property
    def site_cfs_link(self):
        return self.event.site_link + "/cfs"

    def __repr__(self):
        return '<Session %r>' % self.title

    def __setattr__(self, name, value):
        if name == 'short_abstract' or name == 'long_abstract' or name == 'comments':
            super().__setattr__(name, clean_html(clean_up_string(value), allow_link=True))
        else:
            super().__setattr__(name, value)


@event.listens_for(Session, 'before_update')
def receive_after_update(mapper, connection, target):
    target.last_modified_at = datetime.datetime.now(pytz.utc)
