from app.models import db


class Invite(db.Model):
    """invite model class"""
    __tablename__ = 'invites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship("User", backref="invite")
    event_id = db.Column(
        db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id', ondelete='CASCADE'))
    session = db.relationship("Session", backref="invite")
    hash = db.Column(db.String, nullable=False)

    def __init__(self, event_id=None, user_id=None, session_id=None):
        self.user_id = user_id
        self.event_id = event_id
        self.session_id = session_id

    def __repr__(self):
        return '<Invite %r>' % self.user_id

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return 'Invite for %s' % self.session

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""

        return {'id': self.id, 'user_id': self.user_id, 'session_id': self.session_id}
