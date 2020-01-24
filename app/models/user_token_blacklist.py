from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.sql import func as sql_func

from app.models import db


@dataclass(unsafe_hash=True)
class UserTokenBlackListTime(db.Model):
    """user token blacklist time model class"""

    __tablename__ = 'user_token_blacklist_time'
    __table_args__ = (db.UniqueConstraint('user_id', name='user_blacklist_time_uc'),)

    id: int = db.Column(db.Integer, primary_key=True)
    created_at: datetime = db.Column(
        db.DateTime(timezone=True), default=sql_func.now(), nullable=False
    )
    blacklisted_at: datetime = db.Column(
        db.DateTime(timezone=True), default=sql_func.now(), nullable=False
    )
    user_id: int = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False
    )
    user = db.relationship(
        "User", backref="token_blacklist_times", foreign_keys=[user_id]
    )
