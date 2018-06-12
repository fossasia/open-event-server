from app.models import db
from sqlalchemy import desc

DEFAULT_FEE = 0.0


class TicketFees(db.Model):
    "Persists service and maximum fees for a currency"
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
        return '<Ticket Fee {}>'.format(self.service_fee)

    def __str__(self):
        return self.__repr__()


def get_fee(currency):
    "Returns the fee for a given currency string as a float from 0 to 1"
    fee = db.session.query(TicketFees) \
                    .filter(TicketFees.currency == currency) \
                    .order_by(desc(TicketFees.id)).first()

    if fee:
        return fee.service_fee

    return DEFAULT_FEE
