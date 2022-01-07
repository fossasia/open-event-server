from citext import CIText

from app.models import db
from app.models.base import SoftDeletionModel
from app.models.helpers.timestamp import Timestamp
from app.models.helpers.versioning import clean_html, clean_up_string


class Speaker(SoftDeletionModel, Timestamp):
    """Speaker model class"""

    __tablename__ = 'speaker'
    __table_args__ = (
        db.UniqueConstraint(
            'event_id', 'email', 'deleted_at', name='uq_speaker_event_email'
        ),
        db.Index('speaker_event_idx', 'event_id'),
    )
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    photo_url = db.Column(db.String)
    thumbnail_image_url = db.Column(db.String)
    small_image_url = db.Column(db.String)
    icon_image_url = db.Column(db.String)
    short_biography = db.Column(db.Text)
    long_biography = db.Column(db.Text)
    speaking_experience = db.Column(db.Text)
    email = db.Column(CIText)
    mobile = db.Column(db.String)
    website = db.Column(db.String)
    twitter = db.Column(db.String)
    facebook = db.Column(db.String)
    github = db.Column(db.String)
    mastodon = db.Column(db.String)
    linkedin = db.Column(db.String)
    instagram = db.Column(db.String)
    organisation = db.Column(db.String)
    is_featured = db.Column(db.Boolean, default=False)
    is_email_overridden = db.Column(
        db.Boolean, default=False, nullable=False, server_default='False'
    )
    position = db.Column(db.String)
    country = db.Column(db.String)
    city = db.Column(db.String)
    address = db.Column(db.String)
    gender = db.Column(db.String)
    order = db.Column(db.Integer, default=0, nullable=False)
    heard_from = db.Column(db.String)
    sponsorship_required = db.Column(db.Text)
    complex_field_values = db.Column(db.JSON)
    speaker_positions = db.Column(db.JSON)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))

    @staticmethod
    def get_service_name():
        return 'speaker'

    def __repr__(self):
        return '<Speaker %r>' % self.name

    def __setattr__(self, name, value):
        if (
            name == 'short_biography'
            or name == 'long_biography'
            or name == 'speaking_experience'
            or name == 'sponsorship_required'
        ):
            super().__setattr__(name, clean_html(clean_up_string(value)))
        else:
            super().__setattr__(name, value)
