from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    logo = db.Column(db.String)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    location_name = db.Column(db.String)

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


class Sponsor(db.Model):
    __tablename__ = 'sponsors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    url = db.Column(db.String)
    logo = db.Column(db.String)

    def __init__(self, name=None, url=None, logo=None, ):
        self.name = name
        self.url = url
        self.logo = logo

    def __repr__(self):
        return '<Sponsor %r>' % (self.name)


class Speaker(db.Model):
    __tablename__ = 'speakers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return '<Speaker %r>' % (self.name)


class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return '<Session %r>' % (self.name)
