from datetime import datetime

from flask_jwt_extended import current_user

from app.models import db
from app.models.base import SoftDeletionModel
from app.models.user_follow_group import UserFollowGroup


class Group(SoftDeletionModel):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False
    )
    social_links = db.Column(db.JSON)
    logo_url = db.Column(db.String)
    banner_url = db.Column(db.String)
    about = db.Column(db.Text)
    created_at: datetime = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    modified_at: datetime = db.Column(
        db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    user = db.relationship('User', backref='groups')
    roles = db.relationship("UsersGroupsRoles", backref="group")

    owner = db.relationship(
        'User',
        viewonly=True,
        secondary='join(UsersGroupsRoles, Role,'
        ' and_(Role.id == UsersGroupsRoles.role_id, Role.name == "owner"))',
        primaryjoin='UsersGroupsRoles.group_id == Group.id',
        secondaryjoin='User.id == UsersGroupsRoles.user_id',
        backref='owner_groups',
        sync_backref=False,
        uselist=False,
    )

    organizers = db.relationship(
        'User',
        viewonly=True,
        secondary='join(UsersGroupsRoles, Role,'
        ' and_(Role.id == UsersGroupsRoles.role_id, Role.name == "organizer"))',
        primaryjoin='UsersGroupsRoles.group_id == Group.id',
        secondaryjoin='User.id == UsersGroupsRoles.user_id',
        backref='organizer_groups',
        sync_backref=False,
    )

    coorganizers = db.relationship(
        'User',
        viewonly=True,
        secondary='join(UsersGroupsRoles, Role,'
        ' and_(Role.id == UsersGroupsRoles.role_id, Role.name == "coorganizer"))',
        primaryjoin='UsersGroupsRoles.group_id == Group.id',
        secondaryjoin='User.id == UsersGroupsRoles.user_id',
        backref='coorganizer_groups',
        sync_backref=False,
    )

    @property
    def follower(self):
        if not current_user:
            return None
        return UserFollowGroup.query.filter_by(user=current_user, group=self).first()
