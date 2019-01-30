from app.models import db
from app.models.base import SoftDeletionModel
from datetime import datetime

class EventOrgaModel(SoftDeletionModel):
    """Event Orga object table"""

    __tablename__ = 'events_orga'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    starts_at = db.Column(db.DateTime(timezone=True))
    payment_currency = db.Column(db.String, nullable=False)

    def __init__(self,
                 name=None,
                 payment_currency=None):

        self.name = name
        self.starts_at = datetime.utcnow()
        self.payment_currency = payment_currency

    def __repr__(self):
        return '<EventOrgaModel %r>' % self.name

    def __str__(self):
        return self.__repr__()

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {'id': self.id,
                'name': self.name,
                'starts_at': self.starts_at,
                'payment_currency': self.payment_currency}
