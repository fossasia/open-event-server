import datetime

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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    created_at = db.Column(db.DateTime)
    expired_at = db.Column(db.DateTime, nullable=True, default=None)
    completed_at = db.Column(db.DateTime, nullable=True, default=None)

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
                 user_id=None,
                 event_id=None):
        self.identifier = identifier
        self.quantity = quantity
        self.amount = amount
        self.address = address
        self.state = state
        self.country = country
        self.user_id = user_id
        self.event_id = event_id
        self.created_at = datetime.datetime.now()

    def __repr__(self):
        return '<Order %r>' % self.id

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.identifier

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {'id': self.id,
                'identifier': self.identifier,
                'quantity': self.quantity,
                'amount': self.amount,
                'address': self.address,
                'state': self.state,
                'country': self.country}
