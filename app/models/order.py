import datetime
import time
import uuid

from app.api.helpers.db import get_count
from app.models import db


def get_new_order_identifier():
    identifier = str(uuid.uuid4())
    count = get_count(Order.query.filter_by(identifier=identifier))
    if count == 0:
        return identifier
    else:
        return get_new_order_identifier()


class OrderTicket(db.Model):
    __tablename__ = 'orders_tickets'
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id', ondelete='CASCADE'), primary_key=True)
    quantity = db.Column(db.Integer)


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String, unique=True)
    amount = db.Column(db.Float)
    address = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    country = db.Column(db.String)
    zipcode = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='SET NULL'))
    event_invoice_id = db.Column(db.Integer, db.ForeignKey('event_invoices.id', ondelete='SET NULL'))
    marketer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    created_at = db.Column(db.DateTime(timezone=True))
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True, default=None)
    trashed_at = db.Column(db.DateTime(timezone=True), nullable=True, default=None)
    transaction_id = db.Column(db.String)
    paid_via = db.Column(db.String)
    payment_mode = db.Column(db.String)
    brand = db.Column(db.String)
    exp_month = db.Column(db.Integer)
    exp_year = db.Column(db.Integer)
    last4 = db.Column(db.String)
    stripe_token = db.Column(db.String)
    paypal_token = db.Column(db.String)
    status = db.Column(db.String)

    discount_code_id = db.Column(
        db.Integer, db.ForeignKey('discount_codes.id', ondelete='SET NULL'), nullable=True, default=None)
    discount_code = db.relationship('DiscountCode', backref='orders')

    event = db.relationship('Event', backref='orders')
    event_invoice = db.relationship('EventInvoice', backref='orders')
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
                 transaction_id=None,
                 paid_via=None,
                 user_id=None,
                 discount_code_id=None,
                 event_id=None,
                 status='pending',
                 payment_mode=None):
        self.identifier = get_new_order_identifier()
        self.quantity = quantity
        self.amount = amount
        self.city = city
        self.address = address
        self.state = state
        self.country = country
        self.zipcode = zipcode
        self.user_id = user_id
        self.event_id = event_id
        self.transaction_id = transaction_id
        self.paid_via = paid_via
        self.created_at = datetime.datetime.utcnow()
        self.discount_code_id = discount_code_id
        self.status = status
        self.payment_mode = payment_mode

    def __repr__(self):
        return '<Order %r>' % self.id

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.identifier

    def get_invoice_number(self):
        return 'O' + str(int(time.mktime(self.created_at.timetuple()))) + '-' + str(self.id)

    @property
    def invoice_number(self):
        return self.get_invoice_number()

    def get_tickets_count(self):
        count = 0
        for order_ticket in self.order_tickets:
            count += order_ticket.quantity
        return count

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
            'transaction_id': self.transaction_id,
            'paid_via': self.paid_via,
            'payment_mode': self.payment_mode,
            'brand': self.brand,
            'exp_month': self.exp_month,
            'exp_year': self.exp_year,
            'last4': self.last4,
        }
