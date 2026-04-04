from dataclasses import dataclass
from datetime import datetime
import hashlib
import secrets

from sqlalchemy.sql import func

from app.models import db
from app.models.base import SoftDeletionModel


@dataclass(init=False, unsafe_hash=True)
class ApiKey(SoftDeletionModel):
    __tablename__ = 'api_keys'

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String, nullable=True)
    token_hash: str = db.Column(db.String(64), unique=True, nullable=False)
    prefix: str = db.Column(db.String(16), nullable=False)
    last_used_at: datetime = db.Column(db.DateTime(timezone=True))
    revoked_at: datetime = db.Column(db.DateTime(timezone=True))
    created_at: datetime = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id: int = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False
    )

    user = db.relationship('User', backref='api_keys')

    token: str = None

    @staticmethod
    def generate_token() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_token(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def get_service_name() -> str:
        return 'api_key'
