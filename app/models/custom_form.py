import json
from sqlalchemy.schema import UniqueConstraint

from app.models import db

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
    __table_args__ = (UniqueConstraint('event_id', 'field_identifier', 'form', name='custom_form_identifier'), )
    id = db.Column(db.Integer, primary_key=True)
    field_identifier = db.Column(db.String, nullable=False)
    form = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    is_required = db.Column(db.Boolean)
    is_included = db.Column(db.Boolean)
    is_fixed = db.Column(db.Boolean)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))

    def __init__(self,
                 event_id=None,
                 field_identifier=None,
                 form=None,
                 type=None,
                 is_required=None,
                 is_included=None,
                 is_fixed=None):
        self.event_id = event_id
        self.field_identifier = field_identifier,
        self.form = form,
        self.type = type,
        self.is_required = is_required,
        self.is_included = is_included,
        self.is_fixed = is_fixed

    def __repr__(self):
        return '<CustomForm %r>' % self.id

    def __str__(self):
        return self.__repr__()

    @property
    def serialize(self):
        """Return object data in easily serializable format"""

        return {
            'id': self.id,
            'field_identifier': self.field_identifier,
            'form': self.form,
            'type': self.type,
            'is_required': self.is_required,
            'is_included': self.is_included,
            'is_fixed': self.is_fixed
        }
