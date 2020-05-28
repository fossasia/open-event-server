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

    @staticmethod
    def get_service_name():
        return 'microlocation'

    def __repr__(self):
        return '<Microlocation %r>' % self.name
