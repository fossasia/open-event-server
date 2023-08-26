import base64
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO

import qrcode
from citext import CIText

from app.api.helpers.storage import UPLOAD_PATHS, generate_hash
from app.models import db
from app.models.base import SoftDeletionModel


@dataclass(init=False, unsafe_hash=True)
class TicketHolder(SoftDeletionModel):
    __tablename__ = "ticket_holders"

    id: int = db.Column(db.Integer, primary_key=True)
    firstname: str = db.Column(db.String)
    lastname: str = db.Column(db.String)
    email: str = db.Column(CIText)
    address: str = db.Column(db.String)
    city: str = db.Column(db.String)
    state: str = db.Column(db.String)
    country: str = db.Column(db.String)
    job_title: str = db.Column(db.String)
    phone: str = db.Column(db.String)
    tax_business_info: str = db.Column(db.String)
    billing_address: str = db.Column(db.String)
    home_address: str = db.Column(db.String)
    shipping_address: str = db.Column(db.String)
    company: str = db.Column(db.String)
    work_address: str = db.Column(db.String)
    work_phone: str = db.Column(db.String)
    website: str = db.Column(db.String)
    blog: str = db.Column(db.String)
    twitter: str = db.Column(db.String)
    facebook: str = db.Column(db.String)
    instagram: str = db.Column(db.String)
    linkedin: str = db.Column(db.String)
    github: str = db.Column(db.String)
    gender: str = db.Column(db.String)
    accept_video_recording: bool = db.Column(db.Boolean)
    accept_share_details: bool = db.Column(db.Boolean)
    accept_receive_emails: bool = db.Column(db.Boolean)
    age_group: str = db.Column(db.String)
    home_wiki: str = db.Column(db.String)
    wiki_scholarship: str = db.Column(db.String)
    birth_date: datetime = db.Column(db.DateTime(timezone=True))
    pdf_url: str = db.Column(db.String)
    ticket_id: int = db.Column(
        db.Integer, db.ForeignKey('tickets.id', ondelete='CASCADE'), nullable=False
    )
    order_id: int = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'))
    is_checked_in: bool = db.Column(db.Boolean, default=False)
    is_checked_out: bool = db.Column(db.Boolean, default=False)
    is_registered: bool = db.Column(db.Boolean, default=False)
    device_name_checkin: str = db.Column(db.String)
    checkin_times: str = db.Column(db.String)
    checkout_times: str = db.Column(db.String)
    register_times: str = db.Column(db.String)
    attendee_notes: str = db.Column(db.String)
    event_id: int = db.Column(
        db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False
    )
    created_at: datetime = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    modified_at: datetime = db.Column(
        db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    complex_field_values: str = db.Column(db.JSON)
    is_consent_of_refund_policy: bool = db.Column(db.Boolean, default=False)
    native_language: str = db.Column(db.JSON)
    fluent_language: str = db.Column(db.JSON)
    user = db.relationship(
        'User',
        foreign_keys=[email],
        primaryjoin='User.email == TicketHolder.email',
        viewonly=True,
        backref='attendees',
        sync_backref=False,
    )
    order = db.relationship('Order', backref='ticket_holders')
    ticket = db.relationship('Ticket', backref='ticket_holders')
    is_consent_form_field: bool = db.Column(db.Boolean, default=False)
    is_consent_form_field_photo: bool = db.Column(db.Boolean, default=False)
    is_consent_form_field_email: bool = db.Column(db.Boolean, default=False)
    is_badge_printed: bool = db.Column(db.Boolean, default=False)
    badge_printed_at: datetime = db.Column(db.DateTime(timezone=True))
    is_discount_applied: bool = db.Column(db.Boolean, default=False)
    is_access_code_applied: bool = db.Column(db.Boolean, default=False)
    tag_id: int = db.Column(db.Integer, db.ForeignKey('tags.id', ondelete='CASCADE'))
    tag = db.relationship('Tag', backref='ticket_holders')

    @property
    def name(self):
        firstname = self.firstname if self.firstname else ''
        lastname = self.lastname if self.lastname else ''
        if firstname and lastname:
            return f'{firstname} {lastname}'
        else:
            return ''

    @property
    def qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=0,
        )
        qr.add_data(self.order.identifier + "-" + str(self.id))
        qr.make(fit=True)
        img = qr.make_image()

        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        img_str = str(base64.b64encode(buffer.getvalue()), 'utf-8')
        return img_str

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'email': self.email,
            'city': self.city,
            'address': self.address,
            'state': self.state,
            'country': self.country,
            'company': self.company,
            'taxBusinessInfo': self.tax_business_info,
        }

    @property
    def pdf_url_path(self) -> str:
        key = UPLOAD_PATHS['pdf']['tickets_all'].format(
            identifier=self.order.identifier, extra_identifier=self.id
        )
        return (
            f'generated/tickets/{key}/{generate_hash(key)}/'
            + self.order.identifier
            + '.pdf'
        )
