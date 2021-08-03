from app.models import db
from app.models.helpers.timestamp import Timestamp


class UserFollowGroup(db.Model, Timestamp):
    __tablename__ = 'user_follow_groups'
    __table_args__ = (db.UniqueConstraint('group_id', 'user_id', name='uq_group_user'),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False
    )
    user = db.relationship('User', backref='followed_groups')
    group_id = db.Column(
        db.Integer, db.ForeignKey('groups.id', ondelete='CASCADE'), nullable=False
    )
    group = db.relationship("Group", backref='followers')
