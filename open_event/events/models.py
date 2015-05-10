from open_event import db

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
