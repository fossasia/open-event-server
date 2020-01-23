from datetime import datetime
from dataclasses import dataclass
from app.models import db
from app.models.base import SoftDeletionModel

TICKET = 'ticket'
EVENT = 'event'


@dataclass(init=True, repr=True, unsafe_hash=True)
class AccessCode(SoftDeletionModel):
    __tablename__ = "access_codes"

    id: int = db.Column(db.Integer, primary_key=True)
    code: str = db.Column(db.String)
    access_url: str = db.Column(db.String)
    is_active: bool = db.Column(db.Boolean)
    tickets_number: int = db.Column(db.Integer)  # For event level access this holds the max. uses
    min_quantity: int = db.Column(db.Integer)
    max_quantity: int = db.Column(db.Integer)  # For event level access this holds the months for which it is valid
    valid_from: datetime = db.Column(db.DateTime(timezone=True), nullable=True)
    valid_till: datetime = db.Column(db.DateTime(timezone=True), nullable=True)
    ticket_id: int = db.Column(db.Integer, db.ForeignKey('tickets.id', ondelete='CASCADE'))
    event_id: int = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    created_at: datetime = db.Column(db.DateTime(timezone=True))
    marketer_id: int = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

    marketer = db.relationship('User', backref='access_codes_')
    ticket = db.relationship('Ticket', backref='access_code', foreign_keys=[ticket_id])
    event = db.relationship('Event', backref='access_codes', foreign_keys=[event_id])


    @staticmethod
    def get_service_name():
        return 'access_code'

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {'id': self.id,
                'code': self.code,
                'access_url': self.access_url,
                'tickets_number': self.tickets_number,
                'min_quantity': self.min_quantity,
                'max_quantity': self.max_quantity,
                'used_for': self.used_for,
                'valid_from': self.valid_from,
                'valid_till': self.valid_till,
                'event_id': self.event_id,
                'is_active': self.is_active}
