from app.models import db


class BaseModel(db.Model):
    __abstract__ = True

    deleted_at = db.Column(db.DateTime(timezone=True))
