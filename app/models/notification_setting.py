from sqlalchemy_utils import generic_repr

from app.api.helpers.db import get_or_create
from app.models import db
from app.models.helpers.timestamp import Timestamp


@generic_repr
class NotificationSettings(db.Model, Timestamp):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable=False)
    enabled = db.Column(db.Boolean, default=True, nullable=False, server_default='True')

    @staticmethod
    def is_enabled(type: str) -> bool:
        settings, _ = get_or_create(
            NotificationSettings, type=type, defaults=dict(enabled=True)
        )

        return settings.enabled
