import binascii
import os
from argparse import Namespace
from datetime import datetime

import flask_login as login
from flask import current_app
from sqlalchemy import event
from sqlalchemy.sql import func

from app.api.helpers.db import get_count
from app.models import db
from app.models.base import SoftDeletionModel
from app.models.email_notification import EmailNotification
from app.models.event_topic import EventTopic
from app.models.feedback import Feedback
from app.models.helpers.versioning import clean_html, clean_up_string
from app.models.order import Order
from app.models.search import sync
from app.models.session import Session
from app.models.speaker import Speaker
from app.models.ticket import Ticket
from app.models.ticket_fee import get_fee, get_maximum_fee
from app.models.ticket_holder import TicketHolder
from app.models.user import ATTENDEE, ORGANIZER, OWNER


def get_new_event_identifier(length=8):
    identifier = str(binascii.b2a_hex(os.urandom(int(length / 2))), 'utf-8')
    if (
        not identifier.isdigit()
        and get_count(Event.query.filter_by(identifier=identifier)) == 0
    ):
        return identifier
    else:
        return get_new_event_identifier(length)


class Event(SoftDeletionModel):
    """Event object table"""

    __tablename__ = 'events'
    __versioned__ = {'exclude': ['schedule_published_on', 'created_at']}
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String, default=get_new_event_identifier)
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
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    is_promoted = db.Column(db.Boolean, default=False, nullable=False)
    description = db.Column(db.Text)
    original_image_url = db.Column(db.String)
    thumbnail_image_url = db.Column(db.String)
    large_image_url = db.Column(db.String)
    show_remaining_tickets = db.Column(db.Boolean, default=False, nullable=False)
    icon_image_url = db.Column(db.String)
    owner_name = db.Column(db.String)
    is_map_shown = db.Column(db.Boolean)
    has_owner_info = db.Column(db.Boolean)
    owner_description = db.Column(db.String)
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
    event_type_id = db.Column(
        db.Integer, db.ForeignKey('event_types.id', ondelete='CASCADE')
    )
    event_topic_id = db.Column(
        db.Integer, db.ForeignKey('event_topics.id', ondelete='CASCADE')
    )
    event_sub_topic_id = db.Column(
        db.Integer, db.ForeignKey('event_sub_topics.id', ondelete='CASCADE')
    )
    ticket_url = db.Column(db.String)
    db.UniqueConstraint('track.name')
    code_of_conduct = db.Column(db.String)
    schedule_published_on = db.Column(db.DateTime(timezone=True))
    is_ticketing_enabled = db.Column(db.Boolean, default=False)
    is_donation_enabled = db.Column(db.Boolean, default=False)
    is_ticket_form_enabled = db.Column(db.Boolean, default=True, nullable=False)
    payment_country = db.Column(db.String)
    payment_currency = db.Column(db.String)
    paypal_email = db.Column(db.String)
    is_tax_enabled = db.Column(db.Boolean, default=False)
    is_billing_info_mandatory = db.Column(db.Boolean, default=False, nullable=False)
    can_pay_by_paypal = db.Column(db.Boolean, default=False, nullable=False)
    can_pay_by_stripe = db.Column(db.Boolean, default=False, nullable=False)
    can_pay_by_cheque = db.Column(db.Boolean, default=False, nullable=False)
    can_pay_by_bank = db.Column(db.Boolean, default=False, nullable=False)
    can_pay_onsite = db.Column(db.Boolean, default=False, nullable=False)
    can_pay_by_omise = db.Column(db.Boolean, default=False, nullable=False)
    can_pay_by_alipay = db.Column(db.Boolean, default=False, nullable=False)
    can_pay_by_paytm = db.Column(db.Boolean, default=False, nullable=False)
    cheque_details = db.Column(db.String)
    bank_details = db.Column(db.String)
    onsite_details = db.Column(db.String)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    pentabarf_url = db.Column(db.String)
    ical_url = db.Column(db.String)
    xcal_url = db.Column(db.String)
    is_sponsors_enabled = db.Column(db.Boolean, default=False)
    refund_policy = db.Column(
        db.String, default='All sales are final. No refunds shall be issued in any case.'
    )
    is_stripe_linked = db.Column(db.Boolean, default=False)
    discount_code_id = db.Column(
        db.Integer, db.ForeignKey('discount_codes.id', ondelete='CASCADE')
    )
    discount_code = db.relationship(
        'DiscountCode', backref='events', foreign_keys=[discount_code_id]
    )
    event_type = db.relationship(
        'EventType', backref='event', foreign_keys=[event_type_id]
    )
    event_topic = db.relationship(
        'EventTopic', backref='event', foreign_keys=[event_topic_id]
    )
    event_sub_topic = db.relationship(
        'EventSubTopic', backref='event', foreign_keys=[event_sub_topic_id]
    )
    owner = db.relationship(
        'User',
        viewonly=True,
        secondary='join(UsersEventsRoles, Role,'
        ' and_(Role.id == UsersEventsRoles.role_id, Role.name == "owner"))',
        primaryjoin='UsersEventsRoles.event_id == Event.id',
        secondaryjoin='User.id == UsersEventsRoles.user_id',
        backref='owner_events',
        uselist=False,
    )
    organizers = db.relationship(
        'User',
        viewonly=True,
        secondary='join(UsersEventsRoles, Role,'
        ' and_(Role.id == UsersEventsRoles.role_id, Role.name == "organizer"))',
        primaryjoin='UsersEventsRoles.event_id == Event.id',
        secondaryjoin='User.id == UsersEventsRoles.user_id',
        backref='organizer_events',
    )
    coorganizers = db.relationship(
        'User',
        viewonly=True,
        secondary='join(UsersEventsRoles, Role,'
        ' and_(Role.id == UsersEventsRoles.role_id, Role.name == "coorganizer"))',
        primaryjoin='UsersEventsRoles.event_id == Event.id',
        secondaryjoin='User.id == UsersEventsRoles.user_id',
        backref='coorganizer_events',
    )
    track_organizers = db.relationship(
        'User',
        viewonly=True,
        secondary='join(UsersEventsRoles, Role,'
        ' and_(Role.id == UsersEventsRoles.role_id,'
        ' Role.name == "track_organizer"))',
        primaryjoin='UsersEventsRoles.event_id == Event.id',
        secondaryjoin='User.id == UsersEventsRoles.user_id',
        backref='track_organizer_events',
    )
    registrars = db.relationship(
        'User',
        viewonly=True,
        secondary='join(UsersEventsRoles, Role,'
        ' and_(Role.id == UsersEventsRoles.role_id, Role.name == "registrar"))',
        primaryjoin='UsersEventsRoles.event_id == Event.id',
        secondaryjoin='User.id == UsersEventsRoles.user_id',
        backref='registrar_events',
    )
    moderators = db.relationship(
        'User',
        viewonly=True,
        secondary='join(UsersEventsRoles, Role,'
        ' and_(Role.id == UsersEventsRoles.role_id, Role.name == "moderator"))',
        primaryjoin='UsersEventsRoles.event_id == Event.id',
        secondaryjoin='User.id == UsersEventsRoles.user_id',
        backref='moderator_events',
    )
    # staff
    users = db.relationship(
        'User',
        viewonly=True,
        secondary='join(UsersEventsRoles, Role,'
        ' and_(Role.id == UsersEventsRoles.role_id, Role.name != "attendee"))',
        primaryjoin='UsersEventsRoles.event_id == Event.id',
        secondaryjoin='User.id == UsersEventsRoles.user_id',
        backref='events',
    )

    def __init__(self, **kwargs):
        super(Event, self).__init__(**kwargs)

        original_image_url = kwargs.get('original_image_url')
        self.original_image_url = (
            self.set_default_event_image(kwargs.get('event_topic_id'))
            if original_image_url is None
            else original_image_url
        )
        # TODO(Areeb): Test for cleaning up of these on __init__
        self.description = clean_up_string(kwargs.get('description'))
        self.owner_description = clean_up_string(kwargs.get('owner_description'))
        self.code_of_conduct = clean_up_string(kwargs.get('code_of_conduct'))

    def __repr__(self):
        return '<Event %r>' % self.name

    def __setattr__(self, name, value):
        if (
            name == 'owner_description'
            or name == 'description'
            or name == 'code_of_conduct'
        ):
            super(Event, self).__setattr__(name, clean_html(clean_up_string(value)))
        else:
            super(Event, self).__setattr__(name, value)

    @classmethod
    def set_default_event_image(cls, event_topic_id):
        if event_topic_id is None:
            return None
        else:
            event_topic = EventTopic.query.filter_by(id=event_topic_id).first()
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
            return (
                EmailNotification.query.filter_by(
                    user_id=(login.current_user.id if not user_id else int(user_id))
                )
                .filter_by(event_id=self.id)
                .first()
            )
        except:
            return None

    def get_average_rating(self):
        avg = (
            db.session.query(func.avg(Feedback.rating))
            .filter_by(event_id=self.id)
            .scalar()
        )
        if avg is not None:
            avg = round(avg, 2)
        return avg

    def is_payment_enabled(self):
        return (
            self.can_pay_by_paypal
            or self.can_pay_by_stripe
            or self.can_pay_by_omise
            or self.can_pay_by_alipay
            or self.can_pay_by_cheque
            or self.can_pay_by_bank
            or self.can_pay_onsite
            or self.can_pay_by_paytm
        )

    @property
    def average_rating(self):
        return self.get_average_rating()

    def get_organizer(self):
        """returns organizer of an event"""
        for role in self.roles:
            if role.role.name == ORGANIZER:
                return role.user
        return None

    def get_owner(self):
        """returns owner of an event"""
        for role in self.roles:
            if role.role.name == OWNER:
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

    @property
    def tickets_sold_object(self):
        obj = (
            db.session.query(Order.event_id)
            .filter_by(event_id=self.id, status='completed')
            .join(TicketHolder)
        )
        return obj

    def calc_tickets_sold_count(self):
        """Calculate total number of tickets sold for the event"""
        return self.tickets_sold_object.count()

    def calc_tickets_sold_prev_month(self):
        """Calculate tickets sold in the previous month"""
        previous_month = datetime.now().month - 1
        return self.tickets_sold_object.filter_by(completed_at=previous_month).count()

    def calc_total_tickets_count(self):
        """Calculate total available tickets for all types of tickets"""
        total_available = (
            db.session.query(func.sum(Ticket.quantity))
            .filter_by(event_id=self.id)
            .scalar()
        )
        if total_available is None:
            total_available = 0
        return total_available

    def calc_revenue(self):
        """Returns total revenues of all completed orders for the given event"""
        revenue = (
            db.session.query(func.sum(Order.amount))
            .filter_by(event_id=self.id, status='completed')
            .scalar()
        )
        if revenue is None:
            revenue = 0
        return revenue

    def calc_monthly_revenue(self):
        """Returns revenue of current month. Invoice sent every 1st of the month for the previous month"""
        previous_month = datetime.now().month - 1
        orders = Order.query.filter_by(event_id=self.id, status='completed').all()
        monthly_revenue = sum(
            o.amount
            for o in orders
            if o.completed_at and o.completed_at.month == previous_month
        )
        return monthly_revenue

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

    @property
    def order_statistics(self):
        return Namespace(id=self.id)

    @property
    def general_statistics(self):
        return Namespace(id=self.id)


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
