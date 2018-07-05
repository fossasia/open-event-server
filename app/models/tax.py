from sqlalchemy.orm import backref

from app.models import db
from app.models.base import SoftDeletionModel


class Tax(SoftDeletionModel):
    """
    Tax Information about an event.
    """
    __tablename__ = 'tax'

    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String)
    name = db.Column(db.String, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    tax_id = db.Column(db.String, nullable=False)
    should_send_invoice = db.Column(db.Boolean, default=False)
    registered_company = db.Column(db.String)
    address = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    zip = db.Column(db.Integer)
    invoice_footer = db.Column(db.String)
    is_tax_included_in_price = db.Column(db.Boolean, default=False)
    is_invoice_sent = db.Column(db.Boolean, default=False)

    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship('Event', backref=backref('tax', uselist=False))

    def __init__(self,
                 country=None,
                 name=None,
                 rate=None,
                 tax_id=None,
                 should_send_invoice=None,
                 registered_company=None,
                 address=None,
                 city=None,
                 state=None,
                 zip=None,
                 invoice_footer=None,
                 is_tax_included_in_price=None,
                 is_invoice_sent=None,
                 event_id=None,
                 deleted_at=None):
        self.country = country
        self.name = name
        self.rate = rate
        self.tax_id = tax_id
        self.should_send_invoice = should_send_invoice
        self.registered_company = registered_company
        self.address = address
        self.city = city
        self.state = state
        self.zip = zip
        self.invoice_footer = invoice_footer
        self.is_tax_included_in_price = is_tax_included_in_price
        self.is_invoice_sent = is_invoice_sent
        self.event_id = event_id
        self.deleted_at = deleted_at

    def __repr__(self):
        return '<Tax %r>' % self.name

    def __str__(self):
        return self.__repr__()

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'country': self.country,
            'name': self.name,
            'rate': self.rate,
            'tax_id': self.tax_id,
            'should_send_invoice': self.should_send_invoice,
            'registered_company': self.registered_company,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip': self.zip,
            'invoice_footer': self.invoice_footer,
            'is_tax_included_in_price': self.is_tax_included_in_price,
            'is_invoice_sent': self.is_invoice_sent
        }
