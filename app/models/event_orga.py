from app.models import db
from app.models.base import SoftDeletionModel
from datetime import datetime

from dataclasses import dataclass

@dataclass(init=True, repr=True, unsafe_hash=True)
class EventOrgaModel(SoftDeletionModel):
    """Event Orga object table"""

    __tablename__ = 'events_orga'

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name: str = db.Column(db.String, nullable=False)
    starts_at: datetime = db.Column(db.DateTime(timezone=True))
    payment_currency: str = db.Column(db.String, nullable=False)


    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {'id': self.id,
                'name': self.name,
                'starts_at': self.starts_at,
                'payment_currency': self.payment_currency}
