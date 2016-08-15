"""Copyright 2015 Rafal Kowalski"""
import binascii
import os

from sqlalchemy import event

from flask.ext import login
from app.helpers.date_formatter import DateFormatter
from app.helpers.helpers import get_count
from app.helpers.versioning import clean_up_string, clean_html
from custom_forms import CustomForms, session_form_str, speaker_form_str
from app.models.email_notifications import EmailNotification
from app.models.user import ATTENDEE
from version import Version
from . import db


def get_new_event_identifier(length=8):
    identifier = binascii.b2a_hex(os.urandom(length / 2))
    count = get_count(Event.query.filter_by(identifier=identifier))
    if count == 0:
        return identifier
    else:
        return get_new_event_identifier()


class EventsUsers(db.Model):
    """Many to Many table Event Users"""
    __tablename__ = 'eventsusers'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(
        db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    editor = db.Column(db.Boolean)
    admin = db.Column(db.Boolean)
    user = db.relationship("User", backref="events_assocs")


class Event(db.Model):
    """Event object table"""
    __tablename__ = 'events'
    __versioned__ = {
        'exclude': ['creator_id', 'schedule_published_on']
    }
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String)
    name = db.Column(db.String, nullable=False)
    event_url = db.Column(db.String)
    email = db.Column(db.String)
    logo = db.Column(db.String)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    timezone = db.Column(db.String, nullable=False, default="UTC")
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    location_name = db.Column(db.String)
    searchable_location_name = db.Column(db.String)
    description = db.Column(db.Text)
    background_url = db.Column(db.String)
    organizer_name = db.Column(db.String)
    show_map = db.Column(db.Integer)
    organizer_description = db.Column(db.String)
    has_session_speakers = db.Column(db.Boolean, default=False)
    in_trash = db.Column(db.Boolean, default=False)
    track = db.relationship('Track', backref="event")
    microlocation = db.relationship('Microlocation', backref="event")
    session = db.relationship('Session', backref="event")
    speaker = db.relationship('Speaker', backref="event")
    sponsor = db.relationship('Sponsor', backref="event")
    users = db.relationship("EventsUsers", backref="event")
    roles = db.relationship("UsersEventsRoles", backref="event")
    role_invites = db.relationship('RoleInvite', back_populates='event')
    privacy = db.Column(db.String, default="public")
    state = db.Column(db.String, default="Draft")
    type = db.Column(db.String)
    topic = db.Column(db.String)
    sub_topic = db.Column(db.String)
    ticket_url = db.Column(db.String)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User')
    db.UniqueConstraint('track.name')
    code_of_conduct = db.Column(db.String)
    schedule_published_on = db.Column(db.DateTime)
    ticket_include = db.Column(db.Boolean, default=False)
    trash_date = db.Column(db.DateTime)
    payment_country = db.Column(db.String)
    payment_currency = db.Column(db.String)
    paypal_email = db.Column(db.String)
    tax_allow = db.Column(db.Boolean, default=False)
    pay_by_paypal = db.Column(db.Boolean, default=False)
    pay_by_stripe = db.Column(db.Boolean, default=False)
    pay_by_cheque = db.Column(db.Boolean, default=False)
    pay_by_bank = db.Column(db.Boolean, default=False)
    pay_onsite = db.Column(db.Boolean, default=False)

    def __init__(self,
                 name=None,
                 logo=None,
                 start_time=None,
                 end_time=None,
                 timezone='UTC',
                 latitude=None,
                 longitude=None,
                 location_name=None,
                 email=None,
                 description=None,
                 event_url=None,
                 background_url=None,
                 organizer_name=None,
                 organizer_description=None,
                 state=None,
                 type=None,
                 privacy=None,
                 topic=None,
                 sub_topic=None,
                 ticket_url=None,
                 creator=None,
                 copyright=None,
                 code_of_conduct=None,
                 schedule_published_on=None,
                 in_trash=False,
                 has_session_speakers=False,
                 show_map=1,
                 searchable_location_name=None,
                 ticket_include=None,
                 trash_date=None,
                 payment_country=None,
                 payment_currency=None,
                 paypal_email=None,
                 call_for_papers=None,
                 pay_by_paypal=None,
                 pay_by_stripe=None,
                 pay_by_cheque=None,
                 identifier=get_new_event_identifier(),
                 pay_by_bank=None,
                 pay_onsite=None):

        self.name = name
        self.logo = logo
        self.email = email
        self.start_time = start_time
        self.end_time = end_time
        self.timezone = timezone
        self.latitude = latitude
        self.longitude = longitude
        self.location_name = location_name
        self.description = clean_up_string(description)
        self.event_url = event_url
        self.background_url = background_url
        self.organizer_name = organizer_name
        self.organizer_description = clean_up_string(organizer_description)
        self.state = state
        self.show_map = show_map
        self.privacy = privacy
        self.type = type
        self.topic = topic
        self.sub_topic = sub_topic
        self.ticket_url = ticket_url
        self.creator = creator
        self.copyright = copyright
        self.code_of_conduct = code_of_conduct
        self.schedule_published_on = schedule_published_on
        self.in_trash = in_trash
        self.has_session_speakers = has_session_speakers
        self.searchable_location_name = searchable_location_name
        self.ticket_include = ticket_include
        self.trash_date = trash_date
        self.payment_country = payment_country
        self.payment_currency = payment_currency
        self.paypal_email = paypal_email
        self.call_for_papers = call_for_papers
        self.pay_by_paypal = pay_by_paypal
        self.pay_by_stripe = pay_by_stripe
        self.pay_by_cheque = pay_by_cheque
        self.pay_by_bank = pay_by_bank
        self.pay_onsite = pay_onsite
        self.identifier = identifier

    def __repr__(self):
        return '<Event %r>' % self.name

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.name

    def __setattr__(self, name, value):
        if name == 'organizer_description' or name == 'description' or name == 'code_of_conduct':
            super(Event, self).__setattr__(name, clean_html(clean_up_string(value)))
        else:
            super(Event, self).__setattr__(name, value)

    def notification_settings(self):
        try:
            return EmailNotification.query.filter_by(user_id=login.current_user.id).filter_by(event_id=self.id).first()
        except:
            return None

    def has_staff_access(self):
        """does user have role other than attendee"""
        access = False
        for _ in self.roles:
            if _.user_id == login.current_user.id:
                if _.role.name != ATTENDEE:
                    access = True
        return access

    def get_staff_roles(self):
        """returns only roles which are staff i.e. not attendee"""
        return [role for role in self.roles if role.role.name != ATTENDEE]

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'name': self.name,
            'logo': self.logo,
            'begin': DateFormatter().format_date(self.start_time),
            'end': DateFormatter().format_date(self.end_time),
            'timezone': self.timezone,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'location_name': self.location_name,
            'email': self.email,
            'description': self.description,
            'event_url': self.event_url,
            'background_url': self.background_url,
            'organizer_name': self.organizer_name,
            'organizer_description': self.organizer_description,
            'has_session_speakers': self.has_session_speakers,
            'privacy': self.privacy,
            'ticket_url': self.ticket_url,
            'code_of_conduct': self.code_of_conduct,
            'schedule_published_on': self.schedule_published_on
        }


# LISTENERS

@event.listens_for(Event, 'after_insert')
def receive_init(mapper, conn, target):
    custom_form = CustomForms(
        event_id=target.id,
        session_form=session_form_str,
        speaker_form=speaker_form_str
    )
    target.custom_forms.append(custom_form)


@event.listens_for(Event, 'after_insert')
def create_version_info(mapper, conn, target):
    """create version instance after event created"""
    version = Version(event_id=target.id)
    target.version = version
