from citext import CIText
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.sql import func

from app.api.helpers.db import get_count
from app.api.helpers.ticketing import is_discount_available, validate_discount_code
from app.models import db
from app.models.base import SoftDeletionModel
from app.models.order import Order
from app.models.ticket import Ticket
from app.models.ticket_holder import TicketHolder


class DiscountCode(SoftDeletionModel):
    __tablename__ = "discount_codes"
    __table_args__ = (
        UniqueConstraint('event_id', 'code', 'deleted_at', name='uq_event_discount_code'),
    )

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(CIText, nullable=False)
    discount_url = db.Column(db.String)
    value = db.Column(db.Float, nullable=False)
    type = db.Column(db.String, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    tickets_number = db.Column(db.Integer)
    min_quantity = db.Column(db.Integer, default=1)
    max_quantity = db.Column(db.Integer, default=100)
    valid_from = db.Column(db.DateTime(timezone=True), nullable=True)
    valid_till = db.Column(db.DateTime(timezone=True), nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship('Event', backref='discount_codes', foreign_keys=[event_id])
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    marketer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    marketer = db.relationship('User', backref='discount_codes_')

    used_for = db.Column(db.String, nullable=False)

    @staticmethod
    def get_service_name() -> str:
        return 'discount_code'

    def __repr__(self) -> str:
        return '<DiscountCode %r>' % self.id

    def get_confirmed_attendees_query(self):
        return (
            TicketHolder.query.filter_by(deleted_at=None)
            .join(Order)
            .filter_by(discount_code_id=self.id)
            .filter(Order.status.in_(['completed', 'placed']))
        )

    @property
    def confirmed_attendees(self):
        return self.get_confirmed_attendees_query().all()

    @property
    def confirmed_attendees_count(self) -> int:
        return get_count(self.get_confirmed_attendees_query())

    @property
    def valid_expire_time(self):
        return self.valid_till or self.event.ends_at

    def get_supported_tickets(self, ticket_ids=None):
        query = Ticket.query.with_parent(self).filter_by(deleted_at=None)
        if ticket_ids:
            query = query.filter(Ticket.id.in_(ticket_ids))
        return query

    def is_available(self, tickets=None, ticket_holders=None):
        return is_discount_available(self, tickets=tickets, ticket_holders=ticket_holders)

    def validate(self, tickets=None, ticket_holders=None, event_id=None):
        return validate_discount_code(
            self, tickets=tickets, ticket_holders=ticket_holders, event_id=event_id
        )
