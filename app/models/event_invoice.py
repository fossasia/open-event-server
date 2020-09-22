import logging
import time

from flask.templating import render_template
from sqlalchemy.sql import func

from app.api.helpers.db import get_new_identifier
from app.api.helpers.files import create_save_pdf
from app.api.helpers.storage import UPLOAD_PATHS
from app.models import db
from app.models.base import SoftDeletionModel
from app.models.order import Order
from app.models.ticket_fee import TicketFees
from app.settings import get_settings
from app.api.helpers.utilities import monthdelta
from app.api.helpers.mail import send_email_for_monthly_fee_payment
from app.api.helpers.notification import send_notif_monthly_fee_payment

logger = logging.getLogger(__name__)


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

    # Payment Fields
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

    def populate(self):
        assert self.event is not None

        self.user = self.event.owner
        self.generate_pdf()

    def generate_pdf(self):
        admin_info = get_settings()
        currency = self.event.payment_currency
        ticket_fee_object = db.session.query(TicketFees).filter_by(currency=currency).first()
        if not ticket_fee_object:
            logger.error('Ticket Fee not found for event id {id}'.format(id=event.id))
            return

        ticket_fee_percentage = ticket_fee_object.service_fee
        ticket_fee_maximum = ticket_fee_object.maximum_fee
        gross_revenue = self.event.calc_monthly_revenue()
        invoice_amount = gross_revenue * (ticket_fee_percentage / 100)
        if invoice_amount > ticket_fee_maximum:
            invoice_amount = ticket_fee_maximum
        self.amount = invoice_amount
        net_revenue = gross_revenue - invoice_amount
        payment_details = {
            'tickets_sold': self.event.tickets_sold,
            'gross_revenue': gross_revenue,
            'net_revenue': net_revenue,
            'amount_payable': invoice_amount,
        }
        # save invoice as pdf
        self.invoice_pdf_url = create_save_pdf(
            render_template(
                'pdf/event_invoice.html',
                user=self.user,
                admin_info=admin_info,
                currency=currency,
                event=self.event,
                ticket_fee_object=ticket_fee_object,
                payment_details=payment_details,
                net_revenue=net_revenue,
            ),
            UPLOAD_PATHS['pdf']['event_invoice'],
            dir_path='/static/uploads/pdf/event_invoices/',
            identifier=self.event.identifier,
        )

        return self.invoice_pdf_url
    
    def send_notification(self):
        prev_month = monthdelta(self.created_at, 1).strftime(
            "%b %Y"
        )  # Displayed as Aug 2016
        app_name = get_settings()['app_name']
        frontend_url = get_settings()['frontend_url']
        link = '{}/invoices/{}'.format(frontend_url, self.identifier)
        send_email_for_monthly_fee_payment(
            self.user.email,
            event.name,
            prev_month,
            self.amount,
            app_name,
            link,
        )
        send_notif_monthly_fee_payment(
            self.user,
            event.name,
            prev_month,
            self.amount,
            app_name,
            link,
            self.event_id,
        )
