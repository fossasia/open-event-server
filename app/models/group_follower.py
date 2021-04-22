from app.models import db
from app.models.helpers.timestamp import Timestamp


class GroupFollower(db.Model, Timestamp):
    __tablename__ = 'group_followers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False
    )
    user = db.relationship('User', backref='groups_followed')
    group_id = db.Column(
        db.Integer, db.ForeignKey('groups.id', ondelete='CASCADE'), nullable=False
    )
    group = db.relationship("Group", backref='followers')
