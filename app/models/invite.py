from app.models import db


class Invite(db.Model):
    """invite model class"""

    __tablename__ = 'invites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship("User", backref="invite")
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id', ondelete='CASCADE'))
    session = db.relationship("Session", backref="invite")
    hash = db.Column(db.String, nullable=False)

    def __repr__(self):
        return '<Invite %r>' % self.user_id
