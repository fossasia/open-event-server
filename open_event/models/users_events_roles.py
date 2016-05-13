from . import db


class UsersEventsRoles(db.Model):
    __tablename__ = 'users_events_roles'
    id = db.Column(db.Integer,
                   primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
