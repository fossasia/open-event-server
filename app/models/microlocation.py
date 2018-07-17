from app.models import db
from app.models.base import SoftDeletionModel


class Microlocation(SoftDeletionModel):
    """Microlocation model class"""
    __tablename__ = 'microlocations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    floor = db.Column(db.Integer)
    room = db.Column(db.String)
    session = db.relationship('Session', backref="microlocation")
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))

    def __init__(self,
                 name=None,
                 latitude=None,
                 longitude=None,
                 floor=None,
                 event_id=None,
                 room=None,
                 deleted_at=None):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.floor = floor
        self.event_id = event_id
        self.room = room
        self.deleted_at = deleted_at

    @staticmethod
    def get_service_name():
        return 'microlocation'

    def __repr__(self):
        return '<Microlocation %r>' % self.name

    def __str__(self):
        return self.__repr__()

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'name': self.name,
            'floor': self.floor
        }
