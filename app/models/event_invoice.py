import time
import uuid
from datetime import datetime

from dataclasses import dataclass
from app.api.helpers.db import get_count
from app.models import db
from app.models.base import SoftDeletionModel


def get_new_identifier():
    identifier = str(uuid.uuid4())
    count = get_count(EventInvoice.query.filter_by(identifier=identifier))
    if count == 0:
        return identifier
    else:
        return get_new_identifier()


@dataclass(init=True, repr=True, unsafe_hash=True)
class EventInvoice(SoftDeletionModel):
    """
    Stripe authorization information for an event.
    """
    __tablename__ = 'event_invoices'

    id: int = db.Column(db.Integer, primary_key=True)
    identifier: str = db.Column(db.String, unique=True)
    amount: float = db.Column(db.Float)
    address: str = db.Column(db.String)
    city: str = db.Column(db.String)
    state: str = db.Column(db.String)
    country: str = db.Column(db.String)
    zipcode: str = db.Column(db.String)

    user_id: int = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    event_id: int = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='SET NULL'))
    order_id: int = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='SET NULL'))

    created_at: datetime = db.Column(db.DateTime(timezone=True))
    completed_at: datetime = db.Column(db.DateTime(timezone=True), nullable=True, default=None)
    transaction_id: str = db.Column(db.String)
    paid_via: str = db.Column(db.String)
    payment_mode: str = db.Column(db.String)
    brand: str = db.Column(db.String)
    exp_month: int = db.Column(db.Integer)
    exp_year: int = db.Column(db.Integer)
    last4: str = db.Column(db.String)
    stripe_token: str = db.Column(db.String)
    paypal_token: str = db.Column(db.String)
    status: str = db.Column(db.String)
    invoice_pdf_url: str = db.Column(db.String)

    event = db.relationship('Event', backref='invoices')

    order = db.relationship('Order', backref='event_invoices', foreign_keys=[order_id])

    user = db.relationship('User', backref='invoices')

    discount_code_id: int = db.Column(db.Integer, db.ForeignKey('discount_codes.id', ondelete='SET NULL'),
                                 nullable=True, default=None)
    discount_code = db.relationship('DiscountCode', backref='event_invoices')

    def get_invoice_number(self):
        return 'I' + str(int(time.mktime(self.created_at.timetuple()))) + '-' + str(self.id)
