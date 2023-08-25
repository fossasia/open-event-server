from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.sql import func

from app.api.helpers.db import get_count
from app.models import db
from app.models.base import SoftDeletionModel
from app.models.order import Order
from app.models.ticket_holder import TicketHolder


@dataclass(init=False, unsafe_hash=True)
class AccessCode(SoftDeletionModel):
    __tablename__ = "access_codes"

    id: int = db.Column(db.Integer, primary_key=True)
    code: str = db.Column(db.String)
    access_url: str = db.Column(db.String)
    is_active: bool = db.Column(db.Boolean)
    tickets_number: int = db.Column(
        db.Integer
    )  # For event level access this holds the max. uses
    min_quantity: int = db.Column(db.Integer)
    max_quantity: int = db.Column(
        db.Integer
    )  # For event level access this holds the months for which it is valid
    valid_from: datetime = db.Column(db.DateTime(timezone=True), nullable=True)
    valid_till: datetime = db.Column(db.DateTime(timezone=True), nullable=True)
    ticket_id: int = db.Column(
        db.Integer, db.ForeignKey('tickets.id', ondelete='CASCADE')
    )
    event_id: int = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    created_at: datetime = db.Column(db.DateTime(timezone=True), default=func.now())
    marketer_id: int = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE')
    )

    marketer = db.relationship('User', backref='access_codes_')
    ticket = db.relationship('Ticket', backref='access_code', foreign_keys=[ticket_id])
    event = db.relationship('Event', backref='access_codes', foreign_keys=[event_id])

    @staticmethod
    def get_service_name():
        return 'access_code'

    @property
    def valid_expire_time(self):
        return self.valid_till or self.event.ends_at

    def get_confirmed_attendees_query(self):
        """
        Get list of attendee who complete order using access code
        @return: list of attendee
        """
        return (
            TicketHolder.query.filter_by(deleted_at=None)
            .filter_by(is_access_code_applied=True)
            .join(Order)
            .filter_by(access_code_id=self.id)
            .filter(Order.status.in_(['completed', 'placed', 'pending', 'initializing']))
        )

    @property
    def confirmed_attendees_count(self) -> int:
        return get_count(self.get_confirmed_attendees_query())
