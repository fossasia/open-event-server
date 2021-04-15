from datetime import datetime

from app.models import db
from app.models.base import SoftDeletionModel


class Group(SoftDeletionModel):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False
    )
    created_at: datetime = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    modified_at: datetime = db.Column(
        db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    user = db.relationship('User', backref='groups')
    roles = db.relationship("UsersGroupsRoles", backref="group")
