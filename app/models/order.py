import datetime
import uuid

import time

from app.api.helpers.db import get_count
from app.models import db
from app.models.base import SoftDeletionModel


def get_new_order_identifier():
    identifier = str(uuid.uuid4())
    count = get_count(Order.query.filter_by(identifier=identifier))
    if count == 0:
        return identifier
    else:
        return get_new_order_identifier()


def get_updatable_fields():
    """
    :return: The list of fields which can be modified by the order user using the pre payment form.
    """
    return ['country', 'address', 'city', 'state', 'zipcode', 'company', 'tax_business_info', 'status', 'paid_via',
            'order_notes', 'deleted_at', 'user', 'payment_mode', 'event', 'discount_code_id', 'discount_code',
            'ticket_holders', 'user', 'tickets_pdf_url', 'is_billing_enabled']


class OrderTicket(SoftDeletionModel):
    __tablename__ = 'orders_tickets'
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id', ondelete='CASCADE'), primary_key=True)
    quantity = db.Column(db.Integer)


class Order(SoftDeletionModel):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String, unique=True)
    amount = db.Column(db.Float, nullable=False, default=0)
    address = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    country = db.Column(db.String)
    zipcode = db.Column(db.String)
    company = db.Column(db.String)
    tax_business_info = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='SET NULL'))
    marketer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    created_at = db.Column(db.DateTime(timezone=True))
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True, default=None)
    trashed_at = db.Column(db.DateTime(timezone=True), nullable=True, default=None)
    transaction_id = db.Column(db.String)
    paid_via = db.Column(db.String)
    payment_mode = db.Column(db.String)
    is_billing_enabled = db.Column(db.Boolean)
    brand = db.Column(db.String)
    exp_month = db.Column(db.Integer)
    exp_year = db.Column(db.Integer)
    last4 = db.Column(db.String)
    stripe_token = db.Column(db.String)
    paypal_token = db.Column(db.String)
    status = db.Column(db.String)
    cancel_note = db.Column(db.String, nullable=True)
    order_notes = db.Column(db.String)
    tickets_pdf_url = db.Column(db.String)

    discount_code_id = db.Column(
        db.Integer, db.ForeignKey('discount_codes.id', ondelete='SET NULL'), nullable=True, default=None)
    discount_code = db.relationship('DiscountCode', backref='orders')

    event = db.relationship('Event', backref='orders')
    user = db.relationship('User', backref='orders', foreign_keys=[user_id])
    marketer = db.relationship('User', backref='marketed_orders', foreign_keys=[marketer_id])
    tickets = db.relationship("Ticket", secondary='orders_tickets', backref='order')
    order_tickets = db.relationship("OrderTicket", backref='order')

    def __init__(self,
                 quantity=None,
                 amount=None,
                 address=None,
                 city=None,
                 state=None,
                 country=None,
                 zipcode=None,
                 company=None,
                 tax_business_info=None,
                 transaction_id=None,
                 paid_via=None,
                 is_billing_enabled=False,
                 user_id=None,
                 discount_code_id=None,
                 event_id=None,
                 status='pending',
                 payment_mode=None,
                 deleted_at=None,
                 order_notes=None,
                 tickets_pdf_url=None):
        self.identifier = get_new_order_identifier()
        self.quantity = quantity
        self.amount = amount
        self.city = city
        self.address = address
        self.state = state
        self.country = country
        self.zipcode = zipcode
        self.company = company
        self.tax_business_info = tax_business_info
        self.user_id = user_id
        self.event_id = event_id
        self.transaction_id = transaction_id
        self.paid_via = paid_via
        self.is_billing_enabled = is_billing_enabled
        self.created_at = datetime.datetime.now(datetime.timezone.utc)
        self.discount_code_id = discount_code_id
        self.status = status
        self.payment_mode = payment_mode
        self.deleted_at = deleted_at
        self.order_notes = order_notes
        self.tickets_pdf_url = tickets_pdf_url

    def __repr__(self):
        return '<Order %r>' % self.id

    def __str__(self):
        return str(self.identifier)

    def get_invoice_number(self):
        return 'O' + str(int(time.mktime(self.created_at.timetuple()))) + '-' + str(self.id)

    @property
    def invoice_number(self):
        return self.get_invoice_number()

    @property
    def tickets_count(self):
        return sum([t.quantity for t in self.order_tickets])

    @property
    def is_free(self):
        return self.payment_mode == 'free'

    def get_revenue(self):
        if self.amount:
            return self.amount - min(self.amount * (self.event.fee / 100.0), self.event.maximum_fee)
        else:
            return 0.0

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'identifier': self.identifier,
            'quantity': self.quantity,
            'amount': self.amount,
            'address': self.address,
            'state': self.state,
            'zipcode': self.zipcode,
            'country': self.country,
            'company': self.company,
            'taxBusinessInfo': self.tax_business_info,
            'transaction_id': self.transaction_id,
            'paid_via': self.paid_via,
            'isBillingEnabled': self.is_billing_enabled,
            'payment_mode': self.payment_mode,
            'brand': self.brand,
            'exp_month': self.exp_month,
            'exp_year': self.exp_year,
            'last4': self.last4,
        }
