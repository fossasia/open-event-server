from app.models import db


class UsersGroupsRoles(db.Model):
    __tablename__ = 'users_groups_roles'
    __table_args__ = (
        db.UniqueConstraint(
            'user_id', 'group_id', 'role_id', name='uq_uer_user_group_role'
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    group_id = db.Column(
        db.Integer, db.ForeignKey('groups.id', ondelete='CASCADE'), nullable=False
    )
    group = db.relationship("Group")

    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False
    )
    user = db.relationship("User")

    role_id = db.Column(
        db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), nullable=False
    )
    role = db.relationship("Role")

    def __repr__(self):
        return f'<UER {self.user!r}:{self.group_id!r}:{self.role!r}>'
