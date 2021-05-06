import logging
from datetime import datetime, timedelta

import pytz
from flask.templating import render_template
from sqlalchemy.sql import func

from app.api.helpers.files import create_save_pdf
from app.api.helpers.mail import send_email_for_monthly_fee_payment
from app.api.helpers.notification import notify_monthly_payment
from app.api.helpers.storage import UPLOAD_PATHS
from app.api.helpers.utilities import monthdelta, round_money
from app.models import db
from app.models.base import SoftDeletionModel
from app.models.order import Order
from app.models.setting import Setting
from app.models.ticket_fee import TicketFees
from app.settings import get_settings

logger = logging.getLogger(__name__)


class EventInvoice(SoftDeletionModel):
    DUE_DATE_DAYS = 30
    MIN_AMOUNT = 2  # Minimum amount for which the invoice will be generated

    __tablename__ = 'event_invoices'

    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String, unique=True, nullable=False)
    amount = db.Column(db.Float)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='SET NULL'))

    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    issued_at = db.Column(db.DateTime(timezone=True), nullable=False)

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not self.issued_at:
            self.issued_at = datetime.now()

        if not self.identifier:
            self.identifier = self.get_new_id()

    def __repr__(self):
        return '<EventInvoice {!r} {!r} {!r}>'.format(
            self.id,
            self.identifier,
            self.invoice_pdf_url,
        )

    def get_new_id(self) -> str:
        with db.session.no_autoflush:
            identifier = self.issued_at.strftime('%Y%mU-') + '%06d' % (
                EventInvoice.query.count() + 1
            )
            count = EventInvoice.query.filter_by(identifier=identifier).count()
            if count == 0:
                return identifier
            return self.get_new_id()

    @property
    def previous_month_date(self):
        return monthdelta(self.issued_at, -1)

    @property
    def due_at(self):
        return self.issued_at + timedelta(days=EventInvoice.DUE_DATE_DAYS)

    def populate(self):
        assert self.event is not None

        with db.session.no_autoflush:
            self.user = self.event.owner
            return self.generate_pdf()

    def generate_pdf(self, force=False):
        with db.session.no_autoflush:
            latest_invoice_date = (
                EventInvoice.query.filter_by(event=self.event)
                .filter(EventInvoice.issued_at < self.issued_at)
                .with_entities(func.max(EventInvoice.issued_at))
                .scalar()
            )

            admin_info = Setting.query.first()
            currency = self.event.payment_currency
            ticket_fee_object = (
                TicketFees.query.filter_by(country=self.event.payment_country).first()
                or TicketFees.query.filter_by(country='global').first()
            )
            if not ticket_fee_object:
                logger.error('Ticket Fee not found for event %s', self.event)
                return

            ticket_fee_percentage = ticket_fee_object.service_fee
            ticket_fee_maximum = ticket_fee_object.maximum_fee
            gross_revenue = self.event.calc_revenue(
                start=latest_invoice_date, end=self.issued_at
            )
            invoice_amount = gross_revenue * (ticket_fee_percentage / 100)
            if invoice_amount > ticket_fee_maximum:
                invoice_amount = ticket_fee_maximum
            self.amount = round_money(invoice_amount)
            if not force and self.amount == 0:
                logger.warning(
                    'Invoice amount of Event %s is 0, hence skipping generation',
                    self.event,
                )
                return
            if not force and self.amount < EventInvoice.MIN_AMOUNT:
                logger.warning(
                    'Invoice amount of Event %s is %f which is less than %f, hence skipping generation',
                    self.event,
                    self.amount,
                    EventInvoice.MIN_AMOUNT,
                )
                return
            net_revenue = round_money(gross_revenue - invoice_amount)
            orders_query = self.event.get_orders_query(
                start=latest_invoice_date, end=self.issued_at
            )
            first_order_date = orders_query.with_entities(
                func.min(Order.completed_at)
            ).scalar()
            last_order_date = orders_query.with_entities(
                func.max(Order.completed_at)
            ).scalar()
            payment_details = {
                'tickets_sold': self.event.tickets_sold,
                'gross_revenue': round_money(gross_revenue),
                'net_revenue': round_money(net_revenue),
                'first_date': first_order_date or self.previous_month_date,
                'last_date': last_order_date or self.issued_at,
            }
            self.invoice_pdf_url = create_save_pdf(
                render_template(
                    'pdf/event_invoice.html',
                    user=self.user,
                    admin_info=admin_info,
                    currency=currency,
                    event=self.event,
                    ticket_fee=ticket_fee_object,
                    payment_details=payment_details,
                    net_revenue=net_revenue,
                    invoice=self,
                ),
                UPLOAD_PATHS['pdf']['event_invoice'],
                dir_path='/static/uploads/pdf/event_invoices/',
                identifier=self.identifier,
                extra_identifiers={'event_identifier': self.event.identifier},
                new_renderer=True,
            )

        return self.invoice_pdf_url

    def send_notification(self, follow_up=False):
        prev_month = self.previous_month_date.astimezone(
            pytz.timezone(self.event.timezone)
        ).strftime(
            "%b %Y"
        )  # Displayed as Aug 2016
        app_name = get_settings()['app_name']
        frontend_url = get_settings()['frontend_url']
        link = f'{frontend_url}/event-invoice/{self.identifier}/review'
        currency = self.event.payment_currency
        amount = f"{currency} {self.amount:.2f}"
        send_email_for_monthly_fee_payment(
            self.user,
            self.event.name,
            prev_month,
            amount,
            app_name,
            link,
            follow_up=follow_up,
        )
        if isinstance(follow_up, bool):
            notify_monthly_payment(self, follow_up)
