from sqlalchemy.orm import backref

from app.models import db
from app.models.base import SoftDeletionModel


class Tax(SoftDeletionModel):
    """
    Tax Information about an event.
    """

    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String)
    name = db.Column(db.String, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    tax_id = db.Column(db.String, nullable=False)
    should_send_invoice = db.Column(db.Boolean, default=False)
    registered_company = db.Column(db.String)
    contact_name = db.Column(db.String)
    phone = db.Column(db.String)
    email = db.Column(db.String)
    address = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    zip = db.Column(db.String)
    invoice_footer = db.Column(db.String)
    is_tax_included_in_price = db.Column(db.Boolean, default=False)
    is_invoice_sent = db.Column(db.Boolean, default=False)

    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship('Event', backref=backref('tax', uselist=False))

    def __repr__(self):
        return '<Tax %r>' % self.name
