import json
from . import db


SESSION_FORM = {
    "title": {"include": 1, "require": 1},
    "subtitle": {"include": 0, "require": 0},
    "short_abstract": {"include": 1, "require": 0},
    "long_abstract": {"include": 0, "require": 0},
    "comments": {"include": 1, "require": 0},
    "track": {"include": 0, "require": 0},
    "session_type": {"include": 0, "require": 0},
    "language": {"include": 0, "require": 0},
    "slides": {"include": 1, "require": 0},
    "video": {"include": 0, "require": 0},
    "audio": {"include": 0, "require": 0}
}

SPEAKER_FORM = {
    "name": {"include": 1, "require": 1},
    "email": {"include": 1, "require": 1},
    "photo": {"include": 1, "require": 0},
    "organisation": {"include": 1, "require": 0},
    "position": {"include": 1, "require": 0},
    "country": {"include": 1, "require": 0},
    "short_biography": {"include": 1, "require": 0},
    "long_biography": {"include": 0, "require": 0},
    "mobile": {"include": 0, "require": 0},
    "website": {"include": 1, "require": 0},
    "facebook": {"include": 0, "require": 0},
    "twitter": {"include": 1, "require": 0},
    "github": {"include": 0, "require": 0},
    "linkedin": {"include": 0, "require": 0}
}

session_form_str = json.dumps(SESSION_FORM, separators=(',', ':'))
speaker_form_str = json.dumps(SPEAKER_FORM, separators=(',', ':'))


class CustomForms(db.Model):
    """custom form model class"""
    __tablename__ = 'custom_forms'
    id = db.Column(db.Integer, primary_key=True)
    session_form = db.Column(db.String, nullable=False)
    speaker_form = db.Column(db.String, nullable=False)
    event_id = db.Column(
        db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    events = db.relationship("Event", backref="custom_forms")

    def __init__(self, event_id=None, session_form=None, speaker_form=None):
        self.event_id = event_id
        self.session_form = session_form
        self.speaker_form = speaker_form

    def __repr__(self):
        return '<CustomForm %r>' % self.id

    def __str__(self):
        return str(self).encode('utf-8')

    def __unicode__(self):
        return 'CustomForm %r' % self.id

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""

        return {'id': self.id, 'session_form': self.session_form, 'speaker_form': self.speaker_form}
