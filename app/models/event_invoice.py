import time
import uuid
from datetime import datetime

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


class EventInvoice(SoftDeletionModel):
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

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='SET NULL'))

    created_at = db.Column(db.DateTime(timezone=True))
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True, default=None)
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
    invoice_pdf_url = db.Column(db.String)

    event = db.relationship('Event', backref='invoices')
    user = db.relationship('User', backref='invoices')

    discount_code_id = db.Column(db.Integer, db.ForeignKey('discount_codes.id', ondelete='SET NULL'),
                                 nullable=True, default=None)
    discount_code = db.relationship('DiscountCode', backref='event_invoices')

    def __init__(self,
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
                 invoice_pdf_url=None,
                 payment_mode=None,
                 brand=None,
                 exp_month=None,
                 exp_year=None,
                 last4=None,
                 stripe_token=None,
                 paypal_token=None,
                 deleted_at=None
                 ):
        self.identifier = get_new_identifier()
        self.amount = amount
        self.address = address
        self.state = state
        self.country = country
        self.zipcode = zipcode
        self.city = city
        self.user_id = user_id
        self.event_id = event_id
        self.transaction_id = transaction_id
        self.paid_via = paid_via
        self.created_at = datetime.utcnow()
        self.discount_code_id = discount_code_id
        self.status = 'pending'
        self.invoice_pdf_url = invoice_pdf_url
        self.payment_mode = payment_mode
        self.brand = brand
        self.exp_month = exp_month
        self.exp_year = exp_year
        self.last4 = last4
        self.stripe_token = stripe_token
        self.paypal_token = paypal_token
        self.deleted_at = deleted_at

    def get_invoice_number(self):
        return 'I' + str(int(time.mktime(self.created_at.timetuple()))) + '-' + str(self.id)

    def __repr__(self):
        return '<EventInvoice %r>' % self.invoice_pdf_url

    def __str__(self):
        return self.__repr__()
