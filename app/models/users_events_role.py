from app.models import db
from app.models.base import SoftDeletionModel


class UsersEventsRoles(SoftDeletionModel):
    __tablename__ = 'users_events_roles'

    id = db.Column(db.Integer, primary_key=True)

    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship("User")

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'))
    role = db.relationship("Role")

    def __init__(self, user=None, event=None, role=None, user_id=None, role_id=None, event_id=None, deleted_at=None):
        if user:
            self.user = user
        if event:
            self.event = event
        if role:
            self.role = role
        if user_id:
            self.user_id = user_id
        if role_id:
            self.role_id = role_id
        if event_id:
            self.event_id = event_id
        self.deleted_at = deleted_at

    def __repr__(self):
        return '<UER %r:%r:%r>' % (self.user,
                                   self.event_id,
                                   self.role,)

    def __str__(self):
        return self.__repr__()
