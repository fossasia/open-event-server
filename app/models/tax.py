from sqlalchemy.orm import backref

from . import db


class Tax(db.Model):
    """
    Copyright Information about an event.
    """
    __tablename__ = 'tax'

    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String)
    tax_name = db.Column(db.String, nullable=False)
    tax_rate = db.Column(db.Float, nullable=False)
    tax_id = db.Column(db.String, nullable=False)
    send_invoice = db.Column(db.Boolean, default=False)
    registered_company = db.Column(db.String)
    address = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    zip = db.Column(db.Integer)
    invoice_footer = db.Column(db.String)
    tax_include_in_price = db.Column(db.Boolean, default=False)

    event_id = db.Column(
        db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship(
        'Event', backref=backref('tax', uselist=False))

    def __init__(self,
                 country=None,
                 tax_name=None,
                 tax_rate=None,
                 tax_id=None,
                 send_invoice=None,
                 registered_company=None,
                 address=None,
                 city=None,
                 state=None,
                 zip=None,
                 invoice_footer=None,
                 tax_include_in_price=None,
                 event_id=None):
        self.country = country
        self.tax_name = tax_name
        self.tax_rate = tax_rate
        self.tax_id = tax_id
        self.send_invoice = send_invoice
        self.registered_company = registered_company
        self.address = address
        self.city = city
        self.state = state
        self.zip = zip
        self.invoice_footer = invoice_footer
        self.tax_include_in_price = tax_include_in_price
        self.event_id = event_id

    def __repr__(self):
        return '<Tax %r>' % self.tax_name

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.tax_name
