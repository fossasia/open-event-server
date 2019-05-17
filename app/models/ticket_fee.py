from sqlalchemy import desc

from app.models import db

DEFAULT_FEE = 0.0


class TicketFees(db.Model):
    """Persists service and maximum fees for a currency in a country"""
    __tablename__ = 'ticket_fees'

    id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.String)
    country = db.Column(db.String)
    service_fee = db.Column(db.Float)
    maximum_fee = db.Column(db.Float)

    def __init__(self,
                 country=None,
                 currency=None,
                 service_fee=None,
                 maximum_fee=None):
        self.country = country
        self.currency = currency
        self.service_fee = service_fee
        self.maximum_fee = maximum_fee

    def __repr__(self):
        return '<Ticket Fee {} {}>'.format(self.country, self.service_fee)

    def __str__(self):
        return self.__repr__()


def get_fee(country, currency):
    """Returns the fee for a given country and currency string"""
    fee = db.session.query(TicketFees) \
                    .filter(TicketFees.country == country) \
                    .filter(TicketFees.currency == currency) \
                    .order_by(desc(TicketFees.id)).first()

    if fee:
        return fee.service_fee

    return DEFAULT_FEE


def get_maximum_fee(country, currency):
    """Returns the fee for a given country and currency string"""
    fee = db.session.query(TicketFees) \
                    .filter(TicketFees.country == country) \
                    .filter(TicketFees.currency == currency) \
                    .order_by(desc(TicketFees.id)).first()

    if fee:
        return fee.maximum_fee

    return DEFAULT_FEE
