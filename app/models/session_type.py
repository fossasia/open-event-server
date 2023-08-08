from app.models import db
from app.models.base import SoftDeletionModel


class SessionType(SoftDeletionModel):
    __tablename__ = "session_types"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    length = db.Column(db.String, nullable=False)
    position = db.Column(db.Integer, default=0, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship("Event", backref="session_type", foreign_keys=[event_id])
    sessions = db.relationship('Session', backref="session_type")

    def __repr__(self):
        return '<SessionType %r>' % self.name
