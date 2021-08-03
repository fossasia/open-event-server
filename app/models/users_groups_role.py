import random

from citext import CIText
from flask_jwt_extended import current_user

from app.api.helpers.errors import ForbiddenError
from app.api.helpers.mail import send_email_group_role_invite
from app.models import db
from app.settings import get_settings


def generate_hash():
    hash_ = random.getrandbits(128)
    return str(hash_)


class UsersGroupsRoles(db.Model):
    __tablename__ = 'users_groups_roles'
    __table_args__ = (
        db.UniqueConstraint(
            'user_id', 'group_id', 'role_id', name='uq_ugr_user_group_role'
        ),
        db.UniqueConstraint(
            'email', 'group_id', 'role_id', name='uq_ugr_email_group_role'
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String, default=generate_hash)
    email = db.Column(CIText, nullable=False)
    accepted = db.Column(
        db.Boolean, default=False, nullable=False, server_default='False'
    )

    group_id = db.Column(
        db.Integer, db.ForeignKey('groups.id', ondelete='CASCADE'), nullable=False
    )

    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True
    )
    user = db.relationship("User")

    role_id = db.Column(
        db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), nullable=False
    )
    role = db.relationship("Role")

    def __repr__(self):
        return f'<UGR {self.email!r}:{self.user!r}:{self.group!r}:{self.role!r}>'

    def send_invite(self):
        """
        Send mail to invitee
        """
        group = self.group
        role = self.role
        frontend_url = get_settings()['frontend_url']
        link = f"{frontend_url}/group-invites?token={self.token}"
        if group.user != current_user:
            raise ForbiddenError({'pointer': 'group'}, 'Owner access is required.')

        send_email_group_role_invite(self.email, role.name, group.name, link)
