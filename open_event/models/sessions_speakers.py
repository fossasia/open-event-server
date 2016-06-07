from . import db


class UsersEventsRoles(db.Model):
    __tablename__ = 'sessions_speakers'
    id = db.Column(db.Integer, primary_key=True)
    speaker_id = db.Column(db.Integer, db.ForeignKey('speaker.id'))
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))
    speaker = db.relationship("Speaker", backref="speaker")
