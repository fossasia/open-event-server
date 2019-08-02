from sqlalchemy.sql import func as sql_func

from app.models import db


class UserTokenBlackListTime(db.Model):
    """user token blacklist time model class"""
    __tablename__ = 'user_token_blacklist_time'
    __table_args__ = (db.UniqueConstraint('user_id', name='user_blacklist_time_uc'),)

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), default=sql_func.now(), nullable=False)
    blacklisted_at = db.Column(db.DateTime(timezone=True), default=sql_func.now(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship("User", backref="token_blacklist_times", foreign_keys=[user_id])

    def __init__(self, user_id=None, created_at=None, blacklisted_at=None):
        self.user_id = user_id
        self.created_at = created_at
        self.blacklisted_at = blacklisted_at

    def __str__(self):
        return '<TokenBlackListTime User %s blacklisted at %s>' % (self.user, self.blacklisted_at)
