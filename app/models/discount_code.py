from datetime import datetime
from sqlalchemy.sql import func
from app.api.helpers.db import get_count
from app.models import db
from app.models.base import SoftDeletionModel
from app.models.order import Order
from app.models.ticket_holder import TicketHolder

TICKET = 'ticket'
EVENT = 'event'


class DiscountCode(SoftDeletionModel):
    __tablename__ = "discount_codes"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, nullable=False)
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

    def __init__(
        self,
        code=None,
        discount_url=None,
        value=None,
        type=None,
        tickets_number=None,
        min_quantity=None,
        max_quantity=None,
        valid_from=None,
        valid_till=None,
        is_active=True,
        created_at=None,
        used_for=None,
        event_id=None,
        user_id=None,
        marketer_id=None,
        deleted_at=None,
    ):
        self.code = code
        self.discount_url = discount_url
        self.type = type
        self.value = value
        self.tickets_number = tickets_number
        self.min_quantity = min_quantity
        self.max_quantity = max_quantity
        self.valid_from = valid_from
        self.valid_till = valid_till
        self.event_id = event_id
        self.is_active = is_active
        self.created_at = datetime.utcnow()
        self.used_for = used_for
        self.marketer_id = user_id
        self.marketer_id = marketer_id
        self.deleted_at = deleted_at

    @staticmethod
    def get_service_name():
        return 'discount_code'

    def __repr__(self):
        return '<DiscountCode %r>' % self.id

    def __str__(self):
        return self.__repr__()

    def get_confirmed_attendees_query(self):
        return (
            TicketHolder.query.filter_by(deleted_at=None)
            .join(Order)
            .filter_by(discount_code_id=self.id, deleted_at=None)
            .filter(Order.status.in_(['completed', 'placed']))
        )

    @property
    def confirmed_attendees(self):
        return self.get_confirmed_attendees_query().all()

    @property
    def confirmed_attendees_count(self):
        return get_count(self.get_confirmed_attendees_query())

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'code': self.code,
            'discount_url': self.discount_url,
            'value': self.value,
            'type': self.type,
            'tickets_number': self.tickets_number,
            'min_quantity': self.min_quantity,
            'max_quantity': self.max_quantity,
            'used_for': self.used_for,
            'valid_from': self.valid_from,
            'valid_till': self.valid_till,
            'event_id': self.event_id,
            'is_active': self.is_active,
        }
