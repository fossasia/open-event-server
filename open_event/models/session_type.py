from . import db


class SessionType(db.Model):
    __tablename__ = "session_type"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    length = db.Column(db.Float, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    session_id = db.relationship("Session", back_populates="session_type")

    def __init__(self, name=None, length=None, event_id=None, session_id=None):
        self.name = name
        self.length = length
        self.event_id = event_id
        self.session_id = session_id

    def __repr__(self):
        return '<SessionType %r>' % self.name


    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'length': self.length}
