from . import db


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
