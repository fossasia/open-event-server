import uuid
from datetime import datetime
import time

from app.helpers.helpers import get_count
from . import db

def get_new_identifier():
    identifier = str(uuid.uuid4())
    count = get_count(EventInvoice.query.filter_by(identifier=identifier))
    if count == 0:
        return identifier
    else:
        return get_new_identifier()

class EventInvoice(db.Model):
    """
    Stripe authorization information for an event.
    """
    __tablename__ = 'event_invoices'

    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String, unique=True)
    amount = db.Column(db.Float)
    address = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    country = db.Column(db.String)
    zipcode = db.Column(db.String)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='SET NULL'))

    created_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime, nullable=True, default=None)
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

    event = db.relationship('Event', backref='invoices')
    user = db.relationship('User', backref='invoices')

    def __init__(self,
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
        self.identifier = get_new_identifier()
        self.amount = amount
        self.address = address
        self.state = state
        self.country = country
        self.zipcode = zipcode
        self.user_id = user_id
        self.event_id = event_id
        self.transaction_id = transaction_id
        self.paid_via = paid_via
        self.created_at = datetime.utcnow()
        self.status = 'pending'

    def get_invoice_number(self):
        return 'I' + str(int(time.mktime(self.created_at.timetuple()))) + '-' + str(self.id)

    def __repr__(self):
        return '<EventInvoice %r>' % self.stripe_user_id

    def __str__(self):
        return str(self).encode('utf-8')

    def __unicode__(self):
        return self.stripe_user_id
