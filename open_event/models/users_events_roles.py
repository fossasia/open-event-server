from . import db


class UsersEventsRoles(db.Model):
    __tablename__ = 'users_events_roles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    user = db.relationship("User")
    role = db.relationship("Role")

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return '<UserEventRole %r>' % self.name
