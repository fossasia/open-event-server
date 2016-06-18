from . import db


class SessionType(db.Model):
    __tablename__ = "session_type"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    length = db.Column(db.Float, nullable=False)
    event_id = db.Column(
        db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    events = db.relationship("Event", backref="session_type")
    session = db.relationship('Session', backref="session_type")

    def __init__(self, name=None, length=None, event_id=None):
        self.name = name
        self.length = length
        self.event_id = event_id

    def __repr__(self):
        return '<SessionType %r>' % self.name

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id, 'name': self.name, 'length': self.length}
