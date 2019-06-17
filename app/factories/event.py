import factory

import app.factories.common as common
from app.models.event import db, Event


class EventFactoryBasic(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Event
        sqlalchemy_session = db.session

    name = common.string_
    external_event_url = common.url_
    starts_at = common.dateFuture_
    ends_at = common.dateEndFuture_
    timezone = common.timezone_
    latitude = common.float_
    longitude = common.float_
    logo_url = common.imageUrl_
    location_name = common.string_
    searchable_location_name = common.string_
    description = common.string_
    original_image_url = common.imageUrl_
    organizer_name = common.string_
    is_map_shown = True
    organizer_description = common.string_
    is_sessions_speakers_enabled = True
    privacy = "public"
    state = "draft"
    ticket_url = common.url_
    code_of_conduct = common.string_
    is_ticketing_enabled = True
    payment_country = common.country_
    payment_currency = common.currency_
    paypal_email = common.email_
    is_tax_enabled = True
    can_pay_by_paypal = True
    can_pay_by_stripe = True
    can_pay_by_cheque = True
    can_pay_by_bank = True
    can_pay_onsite = True
    cheque_details = common.string_
    bank_details = common.string_
    onsite_details = common.string_
    is_sponsors_enabled = True
    pentabarf_url = common.url_
    ical_url = common.url_
    xcal_url = common.url_
    event_type_id = None
    event_topic_id = None
    event_sub_topic_id = None
    discount_code_id = None
    order_expiry_time = 10
    refund_policy = 'All sales are final. No refunds shall be issued in any case.'
    is_stripe_linked = False
