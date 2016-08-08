from . import db


class TicketFees(db.Model):
    __tablename__ = 'ticket_fees'

    id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.String)
    service_fee = db.Column(db.Integer)
    extra_fee = db.Column(db.Integer)
    maximum_fee = db.Column(db.Integer)
    processing_fee = db.Column(db.Integer)

    def __init__(self, currency, service_fee, extra_fee, maximum_fee, processing_fee):
        self.currency = currency
        self.service_fee = service_fee
        self.extra_fee = extra_fee
        self.maximum_fee = maximum_fee
        self.processing_fee = processing_fee

    def __repr__(self):
        return '<TicketFees %r>' % self.currency

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.currency
