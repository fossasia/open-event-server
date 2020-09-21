import time

from sqlalchemy.sql import func

from app.api.helpers.db import get_new_identifier
from app.models import db
from app.models.base import SoftDeletionModel


def get_new_id():
    return get_new_identifier(EventInvoice)


class EventInvoice(SoftDeletionModel):
    """
    Stripe authorization information for an event.
    """

    __tablename__ = 'event_invoices'

    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String, unique=True, default=get_new_id)
    amount = db.Column(db.Float)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='SET NULL'))

    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
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
    status = db.Column(db.String, default='due')
    invoice_pdf_url = db.Column(db.String)

    event = db.relationship('Event', backref='invoices')
    user = db.relationship('User', backref='event_invoices')

    def get_invoice_number(self):
        return (
            'I' + str(int(time.mktime(self.created_at.timetuple()))) + '-' + str(self.id)
        )

    def __repr__(self):
        return '<EventInvoice %r>' % self.invoice_pdf_url
