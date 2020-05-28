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

    def __repr__(self):
        return '<UER %r:%r:%r>' % (self.user, self.event_id, self.role,)
