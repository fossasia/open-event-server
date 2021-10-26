from datetime import datetime

from flask_jwt_extended import current_user
from sqlalchemy import func
from sqlalchemy_utils import aggregated

from app.models import db
from app.models.base import SoftDeletionModel
from app.models.user_follow_group import UserFollowGroup
from app.settings import get_settings


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
    thumbnail_image_url = db.Column(db.String)
    is_promoted = db.Column(db.Boolean, default=False, nullable=False)
    about = db.Column(db.Text)
    created_at: datetime = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    modified_at: datetime = db.Column(
        db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    @aggregated(
        'followers', db.Column(db.Integer, default=0, server_default='0', nullable=False)
    )
    def follower_count(self):
        return func.count('1')

    user = db.relationship('User', backref='groups')
    roles = db.relationship("UsersGroupsRoles", backref="group")

    @property
    def follower(self):
        if not current_user:
            return None
        return UserFollowGroup.query.filter_by(user=current_user, group=self).first()

    @property
    def view_page_link(self):
        frontend_url = get_settings()['frontend_url']
        return f"{frontend_url}/g/{self.id}"
