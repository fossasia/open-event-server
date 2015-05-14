from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

db = SQLAlchemy()

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    logo = db.Column(db.String)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    location_name = db.Column(db.String, nullable=False)

    def __init__(self, name=None, logo=None, start_time=None, end_time=None, latitude=None, longitude=None, location_name=None):
        self.name = name
        self.logo = logo
        self.start_time = start_time
        self.end_time = end_time
        self.latitude = latitude
        self.longitude = longitude
        self.location_name = location_name

    def __repr__(self):
        return '<Event %r>' % (self.name)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'start_time': self.start_time,
                'end_time': self.end_time,
                'latitude': self.latitude,
                'longitude': self.longitude,
                'location_name': self.location_name}

speakers = db.Table('speakers_sessions',
    db.Column('speaker_id', db.Integer, db.ForeignKey('speaker.id')),
    db.Column('session_id', db.Integer, db.ForeignKey('session.id'))
)

class Session(db.Model):
    __tablename__ = 'session'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    subtitle = db.Column(db.String)
    abstract = db.Column(db.Text)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.String)
    track = db.relationship("Track", uselist=False, backref="session")
    speakers = db.relationship('Speaker', secondary=speakers,
                                backref=db.backref('sessions', lazy='dynamic'))
    level = db.Column(db.String)
    microlocation = db.relationship("Microlocation", uselist=False, backref="session")

    def __init__(self,
                 title=None,
                 subtitle=None,
                 abstract=None,
                 description=None,
                 start_time=None,
                 end_time=None,
                 type=None,
                 track=None,
                 speakers=None,
                 level=None,
                 microlocation=None):
        self.title = title
        self.subtitle = subtitle
        self.abstract = abstract
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.type = type
        self.track = track
        self.speakers = [speakers]
        self.level = level
        self.microlocation = microlocation

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'title': self.title,
                'subtitle': self.subtitle,
                'abstract': self.abstract,
                'description': self.description,
                'start_time': self.start_time,
                'end_time': self.end_time,
                'type': self.type,
                'track': ({'id': self.track.id, 'name': self.track.name})if self.track else None,
                'speakers': [{'id': speaker.id, 'name': speaker.name} for speaker in self.speakers],
                'level': self.level,
                'microlocation': ({'id': self.microlocation.id, 'name': self.microlocation.name})if self.microlocation else None,
                }

    def __repr__(self):
        return '<Session %r>' % (self.title)


class Track(db.Model):
    __tablename__ = 'tracks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))

    def __init__(self, name=None, description=None):
        self.name = name
        self.description = description

    def __repr__(self):
        return '<Track %r>' % (self.name)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'description': self.description,
                }


class Speaker(db.Model):
    __tablename__ = 'speaker'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    photo = db.Column(db.String)
    biography = db.Column(db.Text, nullable=False)
    email = db.Column(db.String, nullable=False)
    web = db.Column(db.String)
    twitter = db.Column(db.String)
    facebook = db.Column(db.String)
    github = db.Column(db.String)
    linkedin = db.Column(db.String)
    organisation = db.Column(db.String)
    position = db.Column(db.String)
    country = db.Column(db.String)

    def __init__(self,
                 name=None,
                 photo=None,
                 biography=None,
                 email=None,
                 web=None,
                 twitter=None,
                 facebook=None,
                 github=None,
                 linkedin=None,
                 organisation=None,
                 position=None,
                 country=None):
        self.name = name
        self.photo = photo
        self.biography = biography
        self.email = email
        self.web = web
        self.twitter = twitter
        self.facebook = facebook
        self.github = github
        self.linkedin = linkedin
        self.organisation = organisation
        self.position = position
        self.country = country

    def __repr__(self):
        return '<Speaker %r>' % (self.name)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'photo': self.photo,
                'biography': self.biography,
                'email': self.email,
                'web': self.web,
                'twitter': self.twitter,
                'facebook': self.facebook,
                'github': self.github,
                'linkedin': self.linkedin,
                'organisation': self.organisation,
                'position': self.position,
                'country': self.country,
                'sessions': [{'id': session.id, 'title': session.title} for session in self.sessions]
                }


class Sponsor(db.Model):
    __tablename__ = 'sponsors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    url = db.Column(db.String)
    logo = db.Column(db.String)

    def __init__(self, name=None, url=None, logo=None, ):
        self.name = name
        self.url = url
        self.logo = logo

    def __repr__(self):
        return '<Sponsor %r>' % (self.name)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'url': self.url,
                'logo': self.logo,
                }


class Microlocation(db.Model):
    __tablename__ = 'microlocations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    floor = db.Column(db.Integer)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))

    def __init__(self, name=None, latitude=None, longitude=None, floor=None ):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.floor = floor

    def __repr__(self):
        return '<Microlocation %r>' % (self.name)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'latitude': self.latitude,
                'longitude': self.longitude,
                'floor': self.floor
                }
