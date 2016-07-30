import datetime
import time

from . import db


class OrderTicket(db.Model):
    __tablename__ = 'orders_tickets'
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), primary_key=True)
    quantity = db.Column(db.Integer)
    ticket = db.relationship('Ticket')


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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    created_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime, nullable=True, default=None)
    transaction_id = db.Column(db.String)
    paid_via = db.Column(db.String)
    payment_mode = db.Column(db.String)
    brand = db.Column(db.String)
    exp_month = db.Column(db.Integer)
    exp_year = db.Column(db.Integer)
    last4 = db.Column(db.String)
    token = db.Column(db.String)
    status = db.Column(db.String)

    event = db.relationship('Event', backref='orders')
    user = db.relationship('User', backref='orders')
    tickets = db.relationship("OrderTicket")

    def __init__(self,
                 identifier=None,
                 quantity=None,
                 amount=None,
                 address=None,
                 city=city,
                 state=None,
                 country=None,
                 zipcode=None,
                 transaction_id=None,
                 paid_via=None,
                 user_id=None,
                 event_id=None):
        self.identifier = identifier
        self.quantity = quantity
        self.amount = amount
        self.address = address
        self.state = state
        self.country = country
        self.zipcode = zipcode
        self.user_id = user_id
        self.event_id = event_id
        self.transaction_id = transaction_id
        self.paid_via = paid_via
        self.created_at = datetime.datetime.now()

    def __repr__(self):
        return '<Order %r>' % self.id

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.identifier

    def get_invoice_number(self):
        return str(int(time.mktime(self.completed_at.timetuple()))) + '-' + str(self.id)

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
