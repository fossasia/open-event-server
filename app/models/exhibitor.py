from sqlalchemy_utils import generic_repr

from app.models import db
from app.models.helpers.timestamp import Timestamp
from app.models.helpers.versioning import clean_html, clean_up_string


@generic_repr
class Exhibitor(db.Model, Timestamp):
    __tablename__ = 'exhibitors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    url = db.Column(db.String)
    position = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    logo_url = db.Column(db.String)
    banner_url = db.Column(db.String)
    video_url = db.Column(db.String)
    slides_url = db.Column(db.String)
    event_id = db.Column(
        db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False
    )

    def __setattr__(self, name, value):
        if name == 'description':
            super().__setattr__(name, clean_html(clean_up_string(value)))
        else:
            super().__setattr__(name, value)
