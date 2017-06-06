from app.models import db


class Microlocation(db.Model):
    """Microlocation model class"""
    __tablename__ = 'microlocation'
    id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String, nullable=False)
    floor = db.Column(db.Integer)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)  
    session = db.relationship('Session', backref="microlocation")
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))

    def __init__(self,
                 room_name=None,
                 floor=None,
                 latitude=None,
                 longitude=None,
                 event_id=None):
        self.room_name = room_name
        self.latitude = latitude
        self.longitude = longitude
        self.floor = floor
        self.event_id = event_id
        

    @staticmethod
    def get_service_name():
        return 'microlocation'

    def __repr__(self):
        return '<Microlocation %r>' % self.room_name

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.room_name

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'room_name': self.room_name,
            'floor': self.floor
        }
