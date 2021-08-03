from app.models import db


class UsersEventsRoles(db.Model):
    __tablename__ = 'users_events_roles'
    __table_args__ = (
        db.UniqueConstraint(
            'user_id', 'event_id', 'role_id', name='uq_uer_user_event_role'
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    event_id = db.Column(
        db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False
    )

    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False
    )
    user = db.relationship("User")

    role_id = db.Column(
        db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), nullable=False
    )
    role = db.relationship("Role")

    def __repr__(self):
        return f'<UER {self.user!r}:{self.event_id!r}:{self.role!r}>'
