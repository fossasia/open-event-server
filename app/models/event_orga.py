from sqlalchemy.sql import func

from app.models import db
from app.models.base import SoftDeletionModel


class EventOrgaModel(SoftDeletionModel):
    """Event Orga object table"""

    __tablename__ = 'events_orga'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    starts_at = db.Column(db.DateTime(timezone=True), default=func.now())
    payment_currency = db.Column(db.String, nullable=False)

    def __repr__(self):
        return '<EventOrgaModel %r>' % self.name
