from app.models import db


class SessionType(db.Model):
    __tablename__ = "session_types"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    length = db.Column(db.String, nullable=False)
    event_id = db.Column(
        db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship("Event", backref="session_type", foreign_keys=[event_id])
    sessions = db.relationship('Session', backref="session_type")

    def __init__(self, name=None, length=None, event_id=None):
        self.name = name
        self.length = length
        self.event_id = event_id

    def __repr__(self):
        return '<SessionType %r>' % self.name

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.name

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id, 'name': self.name, 'length': self.length}
