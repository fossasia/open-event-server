import binascii
import os
from datetime import datetime

import flask_login as login
import pytz
from flask import current_app
from sqlalchemy import event
from sqlalchemy.sql import func

from app.api.helpers.db import get_count
from app.models import db
from app.models.order import Order
from app.models.ticket_fee import get_fee
from app.models.ticket_fee import get_maximum_fee
from app.models.base import SoftDeletionModel
from app.models.email_notification import EmailNotification
from app.models.feedback import Feedback
from app.models.helpers.versioning import clean_up_string, clean_html
from app.models.user import ATTENDEE, ORGANIZER
from app.models.event_topic import EventTopic
from app.models.session import Session
from app.models.speaker import Speaker
from app.models.search import sync
from app.models.ticket import Ticket
from app.models.ticket_holder import TicketHolder

def get_new_event_identifier(length=8):
    identifier = str(binascii.b2a_hex(os.urandom(int(length / 2))), 'utf-8')
    count = get_count(Event.query.filter_by(identifier=identifier))
    if count == 0:
        return identifier
    else:
        return get_new_event_identifier(length)


class Event(SoftDeletionModel):
    """Event object table"""
    __tablename__ = 'events'
    __versioned__ = {
        'exclude': ['schedule_published_on', 'created_at']
    }
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String)
    name = db.Column(db.String, nullable=False)
    external_event_url = db.Column(db.String)
    logo_url = db.Column(db.String)
    starts_at = db.Column(db.DateTime(timezone=True), nullable=False)
    ends_at = db.Column(db.DateTime(timezone=True), nullable=False)
    timezone = db.Column(db.String, nullable=False, default="UTC")
    is_event_online = db.Column(db.Boolean, default=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    location_name = db.Column(db.String)
    searchable_location_name = db.Column(db.String)
    description = db.Column(db.Text)
    original_image_url = db.Column(db.String)
    thumbnail_image_url = db.Column(db.String)
    large_image_url = db.Column(db.String)
    icon_image_url = db.Column(db.String)
    organizer_name = db.Column(db.String)
    is_map_shown = db.Column(db.Boolean)
    has_organizer_info = db.Column(db.Boolean)
    organizer_description = db.Column(db.String)
    is_sessions_speakers_enabled = db.Column(db.Boolean, default=False)
    track = db.relationship('Track', backref="event")
    microlocation = db.relationship('Microlocation', backref="event")
    session = db.relationship('Session', backref="event")
    speaker = db.relationship('Speaker', backref="event")
    sponsor = db.relationship('Sponsor', backref="event")
    tickets = db.relationship('Ticket', backref="event_")
    tags = db.relationship('TicketTag', backref='events')
    roles = db.relationship("UsersEventsRoles", backref="event")
    role_invites = db.relationship('RoleInvite', back_populates='event')
    custom_form = db.relationship('CustomForms', backref="event")
    faqs = db.relationship('Faq', backref="event")
    feedbacks = db.relationship('Feedback', backref="event")
    attendees = db.relationship('TicketHolder', backref="event")
    privacy = db.Column(db.String, default="public")
    state = db.Column(db.String, default="Draft")
    event_type_id = db.Column(db.Integer, db.ForeignKey('event_types.id', ondelete='CASCADE'))
    event_topic_id = db.Column(db.Integer, db.ForeignKey('event_topics.id', ondelete='CASCADE'))
    event_sub_topic_id = db.Column(db.Integer, db.ForeignKey(
        'event_sub_topics.id', ondelete='CASCADE'))
    events_orga_id = db.Column(db.Integer, db.ForeignKey(
        'events_orga.id', ondelete='CASCADE'))
    ticket_url = db.Column(db.String)
    db.UniqueConstraint('track.name')
    code_of_conduct = db.Column(db.String)
    schedule_published_on = db.Column(db.DateTime(timezone=True))
    is_ticketing_enabled = db.Column(db.Boolean, default=False)
    is_donation_enabled = db.Column(db.Boolean, default=False)
    payment_country = db.Column(db.String)
    payment_currency = db.Column(db.String)
    paypal_email = db.Column(db.String)
    is_tax_enabled = db.Column(db.Boolean, default=False)
    can_pay_by_paypal = db.Column(db.Boolean, default=False)
    can_pay_by_stripe = db.Column(db.Boolean, default=False)
    can_pay_by_cheque = db.Column(db.Boolean, default=False)
    can_pay_by_bank = db.Column(db.Boolean, default=False)
    can_pay_onsite = db.Column(db.Boolean, default=False)
    cheque_details = db.Column(db.String)
    bank_details = db.Column(db.String)
    onsite_details = db.Column(db.String)
    created_at = db.Column(db.DateTime(timezone=True))
    pentabarf_url = db.Column(db.String)
    ical_url = db.Column(db.String)
    xcal_url = db.Column(db.String)
    is_sponsors_enabled = db.Column(db.Boolean, default=False)
    refund_policy = db.Column(db.String, default='All sales are final. No refunds shall be issued in any case.')
    order_expiry_time = db.Column(db.Integer, default=10)
    is_stripe_linked = db.Column(db.Boolean, default=False)
    discount_code_id = db.Column(db.Integer, db.ForeignKey(
        'discount_codes.id', ondelete='CASCADE'))
    discount_code = db.relationship('DiscountCode', backref='events', foreign_keys=[discount_code_id])
    event_type = db.relationship('EventType', backref='event', foreign_keys=[event_type_id])
    event_topic = db.relationship('EventTopic', backref='event', foreign_keys=[event_topic_id])
    event_sub_topic = db.relationship(
        'EventSubTopic', backref='event', foreign_keys=[event_sub_topic_id])
    events_orga = db.relationship(
        'EventOrgaModel', backref='event', foreign_keys=[events_orga_id])
    organizers = db.relationship('User',
                                 viewonly=True,
                                 secondary='join(UsersEventsRoles, Role,'
                                           ' and_(Role.id == UsersEventsRoles.role_id, Role.name == "organizer"))',
                                 primaryjoin='UsersEventsRoles.event_id == Event.id',
                                 secondaryjoin='User.id == UsersEventsRoles.user_id',
                                 backref='organizer_events')
    coorganizers = db.relationship('User',
                                   viewonly=True,
                                   secondary='join(UsersEventsRoles, Role,'
                                             ' and_(Role.id == UsersEventsRoles.role_id, Role.name == "coorganizer"))',
                                   primaryjoin='UsersEventsRoles.event_id == Event.id',
                                   secondaryjoin='User.id == UsersEventsRoles.user_id',
                                   backref='coorganizer_events')
    track_organizers = db.relationship('User',
                                       viewonly=True,
                                       secondary='join(UsersEventsRoles, Role,'
                                                 ' and_(Role.id == UsersEventsRoles.role_id,'
                                                 ' Role.name == "track_organizer"))',
                                       primaryjoin='UsersEventsRoles.event_id == Event.id',
                                       secondaryjoin='User.id == UsersEventsRoles.user_id',
                                       backref='track_organizer_events')
    registrars = db.relationship('User',
                                 viewonly=True,
                                 secondary='join(UsersEventsRoles, Role,'
                                           ' and_(Role.id == UsersEventsRoles.role_id, Role.name == "registrar"))',
                                 primaryjoin='UsersEventsRoles.event_id == Event.id',
                                 secondaryjoin='User.id == UsersEventsRoles.user_id',
                                 backref='registrar_events')
    moderators = db.relationship('User',
                                 viewonly=True,
                                 secondary='join(UsersEventsRoles, Role,'
                                           ' and_(Role.id == UsersEventsRoles.role_id, Role.name == "moderator"))',
                                 primaryjoin='UsersEventsRoles.event_id == Event.id',
                                 secondaryjoin='User.id == UsersEventsRoles.user_id',
                                 backref='moderator_events')
    # staff
    users = db.relationship('User',
                            viewonly=True,
                            secondary='join(UsersEventsRoles, Role,'
                                      ' and_(Role.id == UsersEventsRoles.role_id, Role.name != "attendee"))',
                            primaryjoin='UsersEventsRoles.event_id == Event.id',
                            secondaryjoin='User.id == UsersEventsRoles.user_id',
                            backref='events')

    def __init__(self,
                 name=None,
                 logo_url=None,
                 starts_at=None,
                 ends_at=None,
                 timezone='UTC',
                 is_event_online=False,
                 latitude=None,
                 longitude=None,
                 location_name=None,
                 description=None,
                 external_event_url=None,
                 original_image_url=None,
                 thumbnail_image_url=None,
                 large_image_url=None,
                 icon_image_url=None,
                 organizer_name=None,
                 organizer_description=None,
                 state=None,
                 event_type_id=None,
                 privacy=None,
                 event_topic_id=None,
                 event_sub_topic_id=None,
                 ticket_url=None,
                 copyright=None,
                 code_of_conduct=None,
                 schedule_published_on=None,
                 is_sessions_speakers_enabled=False,
                 is_donation_enabled=False,
                 is_map_shown=False,
                 has_organizer_info=False,
                 searchable_location_name=None,
                 is_ticketing_enabled=None,
                 deleted_at=None,
                 payment_country=None,
                 payment_currency=None,
                 paypal_email=None,
                 speakers_call=None,
                 can_pay_by_paypal=None,
                 can_pay_by_stripe=None,
                 can_pay_by_cheque=None,
                 identifier=None,
                 can_pay_by_bank=None,
                 can_pay_onsite=None,
                 cheque_details=None,
                 bank_details=None,
                 pentabarf_url=None,
                 ical_url=None,
                 xcal_url=None,
                 discount_code_id=None,
                 onsite_details=None,
                 is_tax_enabled=None,
                 is_sponsors_enabled=None,
                 stripe_authorization=None,
                 tax=None,
                 order_expiry_time=None,
                 refund_policy='All sales are final. No refunds shall be issued in any case.',
                 is_stripe_linked=False):

        self.name = name
        self.logo_url = logo_url
        self.starts_at = starts_at
        self.ends_at = ends_at
        self.timezone = timezone
        self.is_event_online = is_event_online
        self.latitude = latitude
        self.longitude = longitude
        self.location_name = location_name
        self.description = clean_up_string(description)
        self.external_event_url = external_event_url
        self.original_image_url = original_image_url
        self.original_image_url = self.set_default_event_image(event_topic_id) if original_image_url is None \
            else original_image_url
        self.thumbnail_image_url = thumbnail_image_url
        self.large_image_url = large_image_url
        self.icon_image_url = icon_image_url
        self.organizer_name = organizer_name
        self.organizer_description = clean_up_string(organizer_description)
        self.state = state
        self.is_map_shown = is_map_shown
        self.has_organizer_info = has_organizer_info
        self.privacy = privacy
        self.event_type_id = event_type_id
        self.event_topic_id = event_topic_id
        self.copyright = copyright
        self.event_sub_topic_id = event_sub_topic_id
        self.ticket_url = ticket_url
        self.code_of_conduct = code_of_conduct
        self.schedule_published_on = schedule_published_on
        self.is_sessions_speakers_enabled = is_sessions_speakers_enabled
        self.searchable_location_name = searchable_location_name
        self.is_ticketing_enabled = is_ticketing_enabled
        self.deleted_at = deleted_at
        self.payment_country = payment_country
        self.payment_currency = payment_currency
        self.paypal_email = paypal_email
        self.speakers_call = speakers_call
        self.can_pay_by_paypal = can_pay_by_paypal
        self.can_pay_by_stripe = can_pay_by_stripe
        self.can_pay_by_cheque = can_pay_by_cheque
        self.can_pay_by_bank = can_pay_by_bank
        self.can_pay_onsite = can_pay_onsite
        self.is_donation_enabled = is_donation_enabled
        self.identifier = get_new_event_identifier()
        self.cheque_details = cheque_details
        self.bank_details = bank_details
        self.pentabarf_url = pentabarf_url
        self.ical_url = ical_url
        self.xcal_url = xcal_url
        self.onsite_details = onsite_details
        self.discount_code_id = discount_code_id
        self.created_at = datetime.now(pytz.utc)
        self.is_tax_enabled = is_tax_enabled
        self.is_sponsors_enabled = is_sponsors_enabled
        self.stripe_authorization = stripe_authorization
        self.tax = tax
        self.order_expiry_time = order_expiry_time
        self.refund_policy = refund_policy
        self.is_stripe_linked = is_stripe_linked

    def __repr__(self):
        return '<Event %r>' % self.name

    def __str__(self):
        return self.__repr__()

    def __setattr__(self, name, value):
        if name == 'organizer_description' or name == 'description' or name == 'code_of_conduct':
            super(Event, self).__setattr__(name, clean_html(clean_up_string(value)))
        else:
            super(Event, self).__setattr__(name, value)

    @classmethod
    def set_default_event_image(self, event_topic_id):
        if event_topic_id is None:
            return None
        else:
            event_topic = EventTopic.query.filter_by(
                id=event_topic_id).first()
            return event_topic.system_image_url

    @property
    def fee(self):
        """
        Returns the fee as a percentage from 0 to 100 for this event
        """
        return get_fee(self.payment_country, self.payment_currency)

    @property
    def maximum_fee(self):
        """
        Returns the maximum fee for this event
        """
        return get_maximum_fee(self.payment_country, self.payment_currency)

    def notification_settings(self, user_id):
        try:
            return EmailNotification.query.filter_by(
                user_id=(login.current_user.id if not user_id else int(user_id))). \
                filter_by(event_id=self.id).first()
        except:
            return None

    def get_average_rating(self):
        avg = db.session.query(func.avg(Feedback.rating)).filter_by(event_id=self.id).scalar()
        if avg is not None:
            avg = round(avg, 2)
        return avg

    @property
    def average_rating(self):
        return self.get_average_rating()

    def get_organizer(self):
        """returns organizer of an event"""
        for role in self.roles:
            if role.role.name == ORGANIZER:
                return role.user
        return None

    def has_staff_access(self, user_id):
        """does user have role other than attendee"""
        for _ in self.roles:
            if _.user_id == (login.current_user.id if not user_id else int(user_id)):
                if _.role.name != ATTENDEE:
                    return True
        return False

    def get_staff_roles(self):
        """returns only roles which are staff i.e. not attendee"""
        return [role for role in self.roles if role.role.name != ATTENDEE]

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def calc_tickets_sold_count(self):
        """Calculate total number of tickets sold for the event"""
        return db.session.query(Order.event_id).filter_by(event_id=self.id, status='completed').join(TicketHolder)\
            .count()

    def calc_total_tickets_count(self):
        """Calculate total available tickets for all types of tickets"""
        total_available = db.session.query(func.sum(Ticket.quantity)).filter_by(event_id=self.id).scalar()
        if total_available is None:
            total_available = 0
        return total_available

    def calc_revenue(self):
        """Returns total revenues of all completed orders for the given event"""
        revenue = db.session.query(func.sum(Order.amount)).filter_by(event_id=self.id, status='completed').scalar()
        if revenue is None:
            revenue = 0
        return revenue

    @property
    def tickets_available(self):
        return self.calc_total_tickets_count()

    @property
    def tickets_sold(self):
        return self.calc_tickets_sold_count()

    @property
    def revenue(self):
        return self.calc_revenue()

    @property
    def has_sessions(self):
        return Session.query.filter_by(event_id=self.id).count() > 0

    @property
    def has_speakers(self):
        return Speaker.query.filter_by(event_id=self.id).count() > 0



@event.listens_for(Event, 'after_update')
@event.listens_for(Event, 'after_insert')
def receive_init(mapper, connection, target):
    """
    listen for the 'init' event
    """
    if current_app.config['ENABLE_ELASTICSEARCH']:
        if target.state == 'published' and target.deleted_at is None:
            sync.mark_event(sync.REDIS_EVENT_INDEX, target.id)
        elif target.deleted_at:
            sync.mark_event(sync.REDIS_EVENT_DELETE, target.id)


@event.listens_for(Event, 'after_delete')
def receive_after_delete(mapper, connection, target):
    """
    listen for the 'after_delete' event
    """
    if current_app.config['ENABLE_ELASTICSEARCH']:
        sync.mark_event(sync.REDIS_EVENT_DELETE, target.id)
