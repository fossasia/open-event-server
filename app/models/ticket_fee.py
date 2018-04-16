from __future__ import unicode_literals

from future.utils import python_2_unicode_compatible

from app.models import db
from utils.compat import u


@python_2_unicode_compatible
class TicketFees(db.Model):
    __tablename__ = 'ticket_fees'

    id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.String)
    service_fee = db.Column(db.Float)
    maximum_fee = db.Column(db.Float)

    def __init__(self, currency=None, service_fee=None, maximum_fee=None):
        self.currency = currency
        self.service_fee = service_fee
        self.maximum_fee = maximum_fee

    def __repr__(self):
        return '<Ticket Fee %r>' % self.service_fee

    def __str__(self):
        return u('Ticket Fee %r' % self.service_fee)
