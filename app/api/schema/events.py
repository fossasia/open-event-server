import pytz
from flask_rest_jsonapi.exceptions import ObjectNotFound
from marshmallow import validate, validates_schema
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship
from pytz import timezone
from sqlalchemy.orm.exc import NoResultFound

from app.api.helpers.errors import UnprocessableEntityError
from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema
from app.models.event import Event
from utils.common import use_defaults


@use_defaults()
class EventSchemaPublic(SoftDeletionSchema):
    class Meta:
        type_ = 'event'
        self_view = 'v1.event_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'v1.event_list'
        inflect = dasherize

    @validates_schema(pass_original=True)
    def validate_timezone(self, data, original_data):
        if 'id' in original_data['data']:
            try:
                event = Event.query.filter_by(id=original_data['data']['id']).one()
            except NoResultFound:
                raise ObjectNotFound({'source': 'data/id'}, "Event id not found")

            if 'timezone' not in data:
                data['timezone'] = event.timezone
        try:
            timezone(data['timezone'])
        except pytz.UnknownTimeZoneError:
            raise UnprocessableEntityError(
                {'pointer': '/data/attributes/timezone'},
                "Unknown timezone: '{}'".format(data['timezone']),
            )

    id = fields.Str(dump_only=True)
    identifier = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    external_event_url = fields.Url(allow_none=True)
    starts_at = fields.DateTime(required=True, timezone=True)
    ends_at = fields.DateTime(required=True, timezone=True)
    timezone = fields.Str(required=True)
    is_event_online = fields.Boolean(default=False)
    latitude = fields.Float(validate=lambda n: -90 <= n <= 90, allow_none=True)
    longitude = fields.Float(validate=lambda n: -180 <= n <= 180, allow_none=True)
    logo_url = fields.Url(allow_none=True)
    location_name = fields.Str(allow_none=True)
    searchable_location_name = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    original_image_url = fields.Url(allow_none=True)
    thumbnail_image_url = fields.Url(dump_only=True)
    large_image_url = fields.Url(dump_only=True)
    icon_image_url = fields.Url(dump_only=True)
    show_remaining_tickets = fields.Bool(allow_none=False, default=False)
    owner_name = fields.Str(allow_none=True)
    is_map_shown = fields.Bool(default=False)
    has_owner_info = fields.Bool(default=False)
    owner_description = fields.Str(allow_none=True)
    is_sessions_speakers_enabled = fields.Bool(default=False)
    privacy = fields.Str(default="public")
    state = fields.Str(
        validate=validate.OneOf(choices=["published", "draft"]),
        allow_none=True,
        default='draft',
    )
    ticket_url = fields.Url(allow_none=True)
    code_of_conduct = fields.Str(allow_none=True)
    schedule_published_on = fields.DateTime(allow_none=True)
    is_featured = fields.Bool(default=False)
    is_promoted = fields.Bool(default=False)
    is_ticket_form_enabled = fields.Bool(default=True)
    payment_country = fields.Str(allow_none=True)
    payment_currency = fields.Str(allow_none=True)
    paypal_email = fields.Str(allow_none=True)
    is_tax_enabled = fields.Bool(default=False)
    is_billing_info_mandatory = fields.Bool(default=False)
    is_donation_enabled = fields.Bool(default=False)
    can_pay_by_paypal = fields.Bool(default=False)
    can_pay_by_stripe = fields.Bool(default=False)
    can_pay_by_cheque = fields.Bool(default=False)
    can_pay_by_bank = fields.Bool(default=False)
    can_pay_onsite = fields.Bool(default=False)
    can_pay_by_omise = fields.Bool(default=False)
    can_pay_by_alipay = fields.Bool(default=False)
    can_pay_by_paytm = fields.Bool(default=False)
    cheque_details = fields.Str(allow_none=True)
    bank_details = fields.Str(allow_none=True)
    onsite_details = fields.Str(allow_none=True)
    is_sponsors_enabled = fields.Bool(default=False)
    created_at = fields.DateTime(dump_only=True, timezone=True)
    pentabarf_url = fields.Url(dump_only=True)
    ical_url = fields.Url(dump_only=True)
    xcal_url = fields.Url(dump_only=True)
    refund_policy = fields.String(
        dump_only=True,
        default='All sales are final. No refunds shall be issued in any case.',
    )
    is_stripe_linked = fields.Boolean(dump_only=True, allow_none=True, default=False)

    tickets = Relationship(
        attribute='tickets',
        self_view='v1.event_ticket',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.ticket_list',
        related_view_kwargs={'event_id': '<id>'},
        schema='TicketSchemaPublic',
        many=True,
        type_='ticket',
    )
    faqs = Relationship(
        attribute='faqs',
        self_view='v1.event_faqs',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.faq_list',
        related_view_kwargs={'event_id': '<id>'},
        schema='FaqSchema',
        many=True,
        type_='faq',
    )
    faq_types = Relationship(
        attribute='faq_types',
        self_view='v1.event_faq_types',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.faq_type_list',
        related_view_kwargs={'event_id': '<id>'},
        schema='FaqTypeSchema',
        many=True,
        type_='faq_type',
    )
    feedbacks = Relationship(
        attribute='feedbacks',
        self_view='v1.event_feedbacks',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.feedback_list',
        related_view_kwargs={'event_id': '<id>'},
        schema='FeedbackSchema',
        many=True,
        type_='feedback',
    )
    ticket_tags = Relationship(
        attribute='ticket_tags',
        self_view='v1.event_ticket_tag',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.ticket_tag_list',
        related_view_kwargs={'event_id': '<id>'},
        schema='TicketTagSchema',
        many=True,
        type_='ticket-tag',
    )
    microlocations = Relationship(
        attribute='microlocation',
        self_view='v1.event_microlocation',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.microlocation_list',
        related_view_kwargs={'event_id': '<id>'},
        schema='MicrolocationSchema',
        many=True,
        type_='microlocation',
    )
    social_links = Relationship(
        attribute='social_link',
        self_view='v1.event_social_link',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.social_link_list',
        related_view_kwargs={'event_id': '<id>'},
        schema='SocialLinkSchema',
        many=True,
        type_='social-link',
    )
    tracks = Relationship(
        attribute='track',
        self_view='v1.event_tracks',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.track_list',
        related_view_kwargs={'event_id': '<id>'},
        schema='TrackSchema',
        many=True,
        type_='track',
    )
    sponsors = Relationship(
        attribute='sponsor',
        self_view='v1.event_sponsor',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.sponsor_list',
        related_view_kwargs={'event_id': '<id>'},
        schema='SponsorSchema',
        many=True,
        type_='sponsor',
    )
    speakers_call = Relationship(
        attribute='speakers_call',
        self_view='v1.event_speakers_call',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.speakers_call_detail',
        related_view_kwargs={'event_id': '<id>'},
        schema='SpeakersCallSchema',
        type_='speakers-call',
    )
    session_types = Relationship(
        attribute='session_type',
        self_view='v1.event_session_types',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.session_type_list',
        related_view_kwargs={'event_id': '<id>'},
        schema='SessionTypeSchema',
        many=True,
        type_='session-type',
    )
    event_copyright = Relationship(
        attribute='copyright',
        self_view='v1.event_copyright',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_copyright_detail',
        related_view_kwargs={'event_id': '<id>'},
        schema='EventCopyrightSchema',
        type_='event-copyright',
    )
    tax = Relationship(
        attribute='tax',
        self_view='v1.event_tax',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.tax_detail',
        related_view_kwargs={'event_id': '<id>'},
        schema='TaxSchema',
        type_='tax',
    )
    sessions = Relationship(
        attribute='session',
        self_view='v1.event_session',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.session_list',
        related_view_kwargs={'event_id': '<id>'},
        schema='SessionSchema',
        many=True,
        type_='session',
    )
    speakers = Relationship(
        attribute='speaker',
        self_view='v1.event_speaker',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.speaker_list',
        related_view_kwargs={'event_id': '<id>'},
        schema='SpeakerSchema',
        many=True,
        type_='speaker',
    )
    event_type = Relationship(
        attribute='event_type',
        self_view='v1.event_event_type',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_type_detail',
        related_view_kwargs={'event_id': '<id>'},
        schema='EventTypeSchema',
        type_='event-type',
    )
    event_topic = Relationship(
        attribute='event_topic',
        self_view='v1.event_event_topic',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_topic_detail',
        related_view_kwargs={'event_id': '<id>'},
        schema='EventTopicSchema',
        type_='event-topic',
    )
    event_sub_topic = Relationship(
        attribute='event_sub_topic',
        self_view='v1.event_event_sub_topic',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_sub_topic_detail',
        related_view_kwargs={'event_id': '<id>'},
        schema='EventSubTopicSchema',
        type_='event-sub-topic',
    )
    custom_forms = Relationship(
        attribute='custom_form',
        self_view='v1.event_custom_forms',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.custom_form_list',
        related_view_kwargs={'event_id': '<id>'},
        schema='CustomFormSchema',
        many=True,
        type_='custom-form',
    )
    owner = Relationship(
        attribute='owner',
        self_view='v1.event_owner',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_detail',
        schema='UserSchemaPublic',
        related_view_kwargs={'event_id': '<id>'},
        type_='user',
    )
    organizers = Relationship(
        attribute='organizers',
        self_view='v1.event_organizers',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_list',
        schema='UserSchemaPublic',
        type_='user',
        many=True,
    )
    coorganizers = Relationship(
        attribute='coorganizers',
        self_view='v1.event_coorganizers',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_list',
        schema='UserSchemaPublic',
        type_='user',
        many=True,
    )
    stripe_authorization = Relationship(
        attribute='stripe_authorization',
        self_view='v1.stripe_authorization_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.stripe_authorization_detail',
        related_view_kwargs={'event_id': '<id>'},
        schema='StripeAuthorizationSchema',
        type_='stripe-authorization',
    )
    order_statistics = Relationship(
        self_view='v1.event_order_statistics',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.order_statistics_event_detail',
        related_view_kwargs={'id': '<id>'},
        schema='OrderStatisticsEventSchema',
        type_='order-statistics-event',
    )
    general_statistics = Relationship(
        self_view='v1.event_general_statistics',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_statistics_general_detail',
        related_view_kwargs={'id': '<id>'},
        schema='EventStatisticsGeneralSchema',
        type_='event-statistics-general',
    )


class EventSchema(EventSchemaPublic):
    class Meta:
        type_ = 'event'
        self_view = 'v1.event_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'v1.event_list'
        inflect = dasherize

    event_invoices = Relationship(
        attribute='invoices',
        self_view='v1.event_event_invoice',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_invoice_list',
        related_view_kwargs={'event_id': '<id>'},
        schema='EventInvoiceSchema',
        many=True,
        type_='event-invoice',
    )
    discount_codes = Relationship(
        attribute='discount_code',
        self_view='v1.event_discount_code',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.discount_code_list',
        related_view_kwargs={'event_id': '<id>'},
        schema='DiscountCodeSchema',
        type_='discount-code',
    )
    track_organizers = Relationship(
        attribute='track_organizers',
        self_view='v1.event_track_organizers',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_list',
        schema='UserSchemaPublic',
        type_='user',
        many=True,
    )
    moderators = Relationship(
        attribute='moderators',
        self_view='v1.event_moderators',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_list',
        schema='UserSchemaPublic',
        type_='user',
        many=True,
    )
    registrars = Relationship(
        attribute='registrars',
        self_view='v1.event_registrars',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_list',
        schema='UserSchemaPublic',
        type_='user',
        many=True,
    )
    orders = Relationship(
        attribute='orders',
        self_view='v1.event_orders',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.orders_list',
        related_view_kwargs={'event_id': '<id>'},
        schema='OrderSchema',
        type_='order',
        many=True,
    )
    role_invites = Relationship(
        attribute='role_invites',
        self_view='v1.event_role_invite',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.role_invite_list',
        related_view_kwargs={'event_id': '<id>'},
        schema='RoleInviteSchema',
        type_='role-invite',
    )
    access_codes = Relationship(
        attribute='access_codes',
        self_view='v1.event_access_codes',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.access_code_list',
        related_view_kwargs={'event_id': '<id>'},
        schema='AccessCodeSchema',
        many=True,
        type_='access-code',
    )
    attendees = Relationship(
        attribute='attendees',
        self_view='v1.event_attendees',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.attendee_list',
        related_view_kwargs={'event_id': '<id>'},
        schema='AttendeeSchema',
        many=True,
        type_='attendee',
    )
