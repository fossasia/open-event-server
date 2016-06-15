"""Copyright 2015 Rafal Kowalski"""
from . import db
from open_event.helpers.date_formatter import DateFormatter

speakers_sessions = db.Table('speakers_sessions', db.Column(
    'speaker_id', db.Integer, db.ForeignKey('speaker.id')), db.Column(
        'session_id', db.Integer, db.ForeignKey('session.id')))


class Level(db.Model):
    """Level Model class"""
    __tablename__ = 'level'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    label_en = db.Column(db.String)
    event_id = db.Column(db.Integer, nullable=False)
    session = db.relationship('Session', backref="level")

    def __init__(self, name=None, label_en=None, event_id=None):
        self.name = name
        self.label_en = label_en
        self.event_id = event_id

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'name': self.name, 'label_en': self.label_en}

    def __repr__(self):
        return '<Level %r>' % (self.name)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.name


class Format(db.Model):
    """Format model class"""
    __tablename__ = 'format'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    label_en = db.Column(db.String, nullable=False)
    session = db.relationship('Session', backref="format")
    event_id = db.Column(db.Integer, nullable=False)

    def __init__(self, name=None, label_en=None, session=None, event_id=None):
        self.name = name
        self.label_en = label_en
        self.event_id = event_id

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'name': self.name, 'label_en': self.label_en}

    def __repr__(self):
        return '<Format %r>' % (self.name)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.name


class Language(db.Model):
    """Language model class"""
    __tablename__ = 'language'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    label_en = db.Column(db.String)
    label_de = db.Column(db.String)
    session = db.relationship('Session', backref="language")
    event_id = db.Column(db.Integer, nullable=False)

    def __init__(self,
                 name=None,
                 label_en=None,
                 label_de=None,
                 session=None,
                 event_id=None):
        self.name = name
        self.label_en = label_en
        self.label_de = label_de
        self.event_id = event_id

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'name': self.name,
                'label_en': self.label_en,
                'label_de': self.label_de}

    def __repr__(self):
        return '<Language %r>' % (self.name)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.name


class Session(db.Model):
    """Session model class"""
    __tablename__ = 'session'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    subtitle = db.Column(db.String)
    abstract = db.Column(db.Text)
    description = db.Column(db.Text, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    track_id = db.Column(db.Integer, db.ForeignKey('tracks.id'))
    speakers = db.relationship(
        'Speaker',
        secondary=speakers_sessions,
        backref=db.backref('sessions', lazy='dynamic'))
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'))
    format_id = db.Column(db.Integer, db.ForeignKey('format.id'))
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'))
    microlocation_id = db.Column(db.Integer, db.ForeignKey('microlocation.id'))

    slides = db.Column(db.String)
    video = db.Column(db.String)
    audio = db.Column(db.String)
    signup_url = db.Column(db.String)

    event_id = db.Column(
        db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    state = db.Column(db.String, default="pending")

    def __init__(self,
                 title=None,
                 subtitle=None,
                 abstract=None,
                 description=None,
                 start_time=None,
                 end_time=None,
                 format=None,
                 track=None,
                 level=None,
                 language=None,
                 microlocation=None,
                 speakers=[],
                 event_id=None,
                 state="pending",
                 slides=None,
                 video=None,
                 audio=None,
                 signup_url=None):
        self.title = title
        self.subtitle = subtitle
        self.abstract = abstract
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.format = format
        self.track = track
        self.level = level
        self.language = language
        self.microlocation = microlocation
        self.speakers = speakers
        self.event_id = event_id
        self.state = state
        self.slides = slides
        self.video = video
        self.audio = audio
        self.signup_url = signup_url

    @property
    def is_accepted(self):
        return self.state == "accepted"

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'title': self.title,
            'subtitle': self.subtitle,
            'abstract': self.abstract,
            'description': self.description,
            'begin': DateFormatter().format_date(self.start_time),
            'end': DateFormatter().format_date(self.end_time),
            'format': {
                'id': self.format.name,
                'label_en': self.format.label_en
            } if self.format else None,
            'track': self.track.id if self.track else None,
            'speakers': [
                {'id': speaker.id,
                 'name': speaker.name} for speaker in self.speakers
            ],
            'level': {
                'id': self.level.name,
                'label_en': self.level.label_en
            } if self.level else None,
            'lang': {
                'id': self.language.name,
                'label_en': self.language.label_en,
                'label_de': self.language.label_de
            } if self.language else None,
            'microlocation': self.microlocation.id
            if self.microlocation else None
        }

    def __repr__(self):
        return '<Session %r>' % self.title

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.title
