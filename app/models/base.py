from app.models import db


class SoftDeletionModel(db.Model):
    """
        Base model for soft deletion support. All the models which support soft deletion should extend it.
    """
    __abstract__ = True

    deleted_at = db.Column(db.DateTime(timezone=True))
