import base64
from io import BytesIO

import qrcode

from app.models import db
from app.models.base import SoftDeletionModel


class TicketHolder(SoftDeletionModel):
    __tablename__ = "ticket_holders"

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String, nullable=False)
    lastname = db.Column(db.String, nullable=False)
    email = db.Column(db.String)
    address = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    country = db.Column(db.String)
    job_title = db.Column(db.String)
    phone = db.Column(db.String)
    tax_business_info = db.Column(db.String)
    billing_address = db.Column(db.String)
    home_address = db.Column(db.String)
    shipping_address = db.Column(db.String)
    company = db.Column(db.String)
    work_address = db.Column(db.String)
    work_phone = db.Column(db.String)
    website = db.Column(db.String)
    blog = db.Column(db.String)
    twitter = db.Column(db.String)
    facebook = db.Column(db.String)
    github = db.Column(db.String)
    gender = db.Column(db.String)
    birth_date = db.Column(db.DateTime(timezone=True))
    pdf_url = db.Column(db.String)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id', ondelete='CASCADE'))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'))
    order = db.relationship('Order', backref='ticket_holders')
    ticket = db.relationship('Ticket', backref='ticket_holders')
    is_checked_in = db.Column(db.Boolean, default=False)
    is_checked_out = db.Column(db.Boolean, default=False)
    device_name_checkin = db.Column(db.String)
    checkin_times = db.Column(db.String)
    checkout_times = db.Column(db.String)
    attendee_notes = db.Column(db.String)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    user = db.relationship('User', foreign_keys=[email], primaryjoin='User.email == TicketHolder.email', viewonly=True,
                           backref='attendees')

    def __init__(self,
                 firstname=None,
                 lastname=None,
                 email=None,
                 address=None,
                 city=None,
                 state=None,
                 country=None,
                 job_title=None,
                 phone=None,
                 tax_business_info=None,
                 billing_address=None,
                 home_address=None,
                 shipping_address=None,
                 company=None,
                 work_address=None,
                 work_phone=None,
                 website=None,
                 blog=None,
                 twitter=None,
                 facebook=None,
                 github=None,
                 gender=None,
                 birth_date=None,
                 ticket_id=None,
                 is_checked_in=False,
                 checkin_times=None,
                 checkout_times=None,
                 is_checked_out=False,
                 device_name_checkin=None,
                 attendee_notes=None,
                 order_id=None,
                 pdf_url=None,
                 event_id=None,
                 deleted_at=None):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.city = city
        self.address = address
        self.state = state
        self.ticket_id = ticket_id
        self.country = country
        self.job_title = job_title
        self.phone = phone
        self.tax_business_info = tax_business_info
        self.billing_address = billing_address
        self.home_address = home_address
        self.shipping_address = shipping_address
        self.company = company
        self.work_address = work_address
        self.work_phone = work_phone
        self.website = website
        self.blog = blog
        self.twitter = twitter
        self.facebook = facebook
        self.github = github
        self.gender = gender
        self.birth_date = birth_date
        self.order_id = order_id
        self.is_checked_in = is_checked_in
        self.checkin_times = checkin_times
        self.checkout_times = checkout_times
        self.is_checked_out = is_checked_out
        self.device_name_checkin = device_name_checkin
        self.attendee_notes = attendee_notes
        self.pdf_url = pdf_url
        self.event_id = event_id
        self.deleted_at = deleted_at

    def __repr__(self):
        return '<TicketHolder %r>' % self.id

    def __str__(self):
        return self.__repr__()

    @property
    def name(self):
        firstname = self.firstname if self.firstname else ''
        lastname = self.lastname if self.lastname else ''
        if firstname and lastname:
            return u'{} {}'.format(firstname, lastname)
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
        return {'id': self.id,
                'firstname': self.firstname,
                'lastname': self.lastname,
                'email': self.email,
                'city': self.city,
                'address': self.address,
                'state': self.state,
                'country': self.country,
                'company': self.company,
                'taxBusinessInfo': self.tax_business_info}
