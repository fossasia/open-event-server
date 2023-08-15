import os.path as path
import sys

import dredd_hooks as hooks
import requests

# DO NOT REMOVE THIS. This adds the project root for successful imports.
# Imports from the project directory should be placed only below this
sys.path.insert(1, path.abspath(path.join(__file__, "../..")))

from flask_migrate import Migrate
from flask import Flask
from app.models import db
from app.models.role import Role
from app.models.user_token_blacklist import (  # noqa
    UserTokenBlackListTime,
)  # Workaround for registering unimported model
from app.api import routes  # noqa Workaround for importing all required models

# imports from factories

from tests.factories.event_location import EventLocationFactory
from tests.factories.badge_field_form import BadgeFieldFormFactory
from tests.factories.badge_form import BadgeFormFactory
from tests.factories.custom_system_role import CustomSysRoleFactory
from tests.factories.panel_permission import PanelPermissionFactory
from tests.factories.user import UserFactory
from tests.factories.notification import NotificationSubFactory
from tests.factories.event import EventFactoryBasic
from tests.factories.group import GroupFactory
from tests.factories.social_link import SocialLinkFactory
from tests.factories.microlocation import MicrolocationFactory, MicrolocationSubFactory
from tests.factories.image_size import EventImageSizeFactory, SpeakerImageSizeFactory
from tests.factories.page import PageFactory
from tests.factories.event_copyright import EventCopyrightFactory
from tests.factories.setting import SettingFactory
from tests.factories.event_type import EventTypeFactory
from tests.factories.discount_code import (
    DiscountCodeFactory,
    DiscountCodeTicketFactory,
    DiscountCodeTicketSubFactory,
)
from tests.factories.access_code import AccessCodeFactory
from tests.factories.custom_form import CustomFormFactory
from tests.factories.faq import FaqFactory
from tests.factories.event_topic import EventTopicFactory
from tests.factories.event_invoice import EventInvoiceFactory
from tests.factories.event_sub_topic import EventSubTopicFactory
from tests.factories.event_role_permission import EventRolePermissionsFactory
from tests.factories.sponsor import SponsorFactory
from tests.factories.speakers_call import SpeakersCallFactory
from tests.factories.tax import TaxFactory
from tests.factories.station import StationFactory, StationSubFactory
from tests.factories.station_store_pax import StationStorePaxFactory
from tests.factories.session import SessionFactory, SessionSubFactory
from tests.factories.speaker import SpeakerFactory
from tests.factories.ticket import TicketFactory, TicketSubFactory
from tests.factories.attendee import (
    AttendeeFactory,
    AttendeeOrderSubFactory,
    AttendeeSubFactory,
)
from tests.factories.session_type import SessionTypeFactory
from tests.factories.track import TrackFactory, TrackFactoryBase
from tests.factories.ticket_tag import TicketTagFactory
from tests.factories.role import RoleFactory
from tests.factories.ticket_fee import TicketFeesFactory
from tests.factories.role_invite import RoleInviteFactory
from tests.factories.users_events_roles import (
    UsersEventsRolesFactory,
    UsersEventsRolesSubFactory,
)
from tests.factories.custom_placeholder import CustomPlaceholderFactory
from tests.factories.user_permission import UserPermissionFactory
from tests.factories.email_notification import EmailNotificationFactory
from tests.factories.activities import ActivityFactory
from tests.factories.stripe_authorization import StripeAuthorizationFactory
from tests.factories.mail import MailFactory
from tests.factories.order import OrderFactory
from tests.factories.faq_type import FaqTypeFactory
from tests.factories.user_email import UserEmailFactory
from tests.factories.feedback import FeedbackFactory
from tests.factories.service import ServiceFactory
from tests.factories.message_setting import MessageSettingsFactory
from tests.factories.user_favourite_events import UserFavouriteEventFactory
from tests.factories.user_favourite_sessions import UserFavouriteSessionFactory
from tests.factories.exhibitor import ExhibitorFactory
from tests.all.integration.api.helpers.order.test_calculate_order_amount import (
    _create_taxed_tickets,
)
from tests.factories.translation_channel import TranslationChannelFactory
from tests.factories.video_stream import VideoStreamFactoryBase

stash = {}
api_username = "open_event_test_user@fossasia.org"
api_password = "fossasia"
api_uri = "http://localhost:5555/v1/auth/login"


def obtain_token():
    data = {"email": api_username, "password": api_password}
    url = api_uri
    response = requests.post(url, json=data)
    response.raise_for_status()
    parsed_body = response.json()
    token = parsed_body["access_token"]
    return token


def create_super_admin(email, password):
    user = UserFactory(
        email=email,
        password=password,
        is_super_admin=True,
        is_admin=True,
        is_verified=True,
    )
    db.session.add(user)
    db.session.commit()
    return user


@hooks.before_all
def before_all(transaction):
    app = Flask(__name__)
    app.config.from_object('config.TestingConfig')
    db.init_app(app)
    Migrate(app, db)
    stash['app'] = app
    stash['db'] = db


@hooks.before_each
def before_each(transaction):
    with stash['app'].app_context():
        db.engine.execute("drop schema if exists public cascade")
        db.engine.execute("create schema public")
        db.engine.execute('create extension if not exists citext')
        db.create_all()
        create_super_admin(api_username, api_password)

    if 'token' in stash:
        print('adding a token')
    else:
        stash['token'] = obtain_token()

    transaction['request']['headers']['Authorization'] = "JWT " + stash['token']


@hooks.after_each
def after_each(transaction):
    with stash['app'].app_context():
        db.session.remove()


# ------------------------- Authentication -------------------------
@hooks.before("Authentication > JWT Authentication > Authenticate and generate token")
@hooks.before("Authentication > JWT Authentication > Authenticate with remember me")
@hooks.before(
    "Authentication > JWT Authentication > Authenticate with remember me for mobile"
)
def skip_auth(transaction):
    """
    POST /v1/auth/login
    :param transaction:
    :return:
    """
    transaction['request']['headers']['Authorization'] = ""
    with stash['app'].app_context():
        user = UserFactory(
            email="email@example.com", password="password", is_verified=True
        )
        db.session.add(user)
        db.session.commit()
        print('User Created')


@hooks.before("Authentication > Re-Authentication > Generate fresh token")
@hooks.before("Authentication > Token Refresh > Access Token Refresh for Web")
@hooks.before("Authentication > Token Refresh > Access Token Refresh for mobile")
def skip_token_refresh(transaction):
    """
    POST /v1/auth/token/refresh
    :param transaction:
    :return:
    """
    transaction['skip'] = True


# ------------------------- Users -------------------------
@hooks.before("Users > Users Collection > List All Users")
def user_get_list(transaction):
    """
    GET /users
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        user = UserFactory()
        db.session.add(user)
        db.session.commit()


@hooks.before("Users > Users Collection > Create User")
def user_post(transaction):
    """
    POST /users
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        user = UserFactory()
        db.session.add(user)
        db.session.commit()


@hooks.before("Users > User Details > Get Details")
def user_get_detail(transaction):
    """
    GET /users/2
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        user = UserFactory()
        db.session.add(user)
        db.session.commit()


@hooks.before("Users > User Details > Update User")
def user_patch(transaction):
    """
    PATCH /users/2
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        user = UserFactory()
        db.session.add(user)
        db.session.commit()


@hooks.before("Users > User Details > Delete User")
def user_delete(transaction):
    """
    DELETE /users/2
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        user = UserFactory()
        db.session.add(user)
        db.session.commit()


@hooks.before(
    "Users > Get User Details for a Notification > Get User Details for a Notification"
)
def user_notification(transaction):
    """
    GET /notifications/1/user
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        NotificationSubFactory()
        db.session.commit()


@hooks.before(
    "Users > Get User Details for an Event Invoice > Get User Details for an Event Invoice"
)
def user_event_invoice(transaction):
    """
    GET /event-invoices/1/user
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_invoice = EventInvoiceFactory()
        db.session.add(event_invoice)
        db.session.commit()


@hooks.before(
    "Users > Get User Details for an Access Code > Get User Details for an Access Code"
)
def user_access_code(transaction):
    """
    GET /access-codes/1/user
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        access_code = AccessCodeFactory()
        db.session.add(access_code)
        db.session.commit()


@hooks.before(
    "Users > Get User Details for an Email Notification > Get User Details for an Email Notification"
)
def user_email_notification(transaction):
    """
    GET /email-notifications/1/user
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        email_notification = EmailNotificationFactory()
        db.session.add(email_notification)
        db.session.commit()


@hooks.before(
    "Users > Get User Details for a Discount Code > Get User Details for a Discount Code"
)
def user_discount_code(transaction):
    """
    GET /discount-codes/1/user
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        discount_code = DiscountCodeFactory()
        db.session.add(discount_code)
        db.session.commit()


@hooks.before("Users > Get User Details for a Speaker > Get User Details for a Speaker")
def user_speaker(transaction):
    """
    GET /speakers/1/user
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        speaker = SpeakerFactory()
        db.session.add(speaker)
        db.session.commit()


@hooks.before("Users Check In > Get Registration Stats > Get Registration Stats")
def get_registration_stats(transaction):
    """
    GET v1/user-check-in/stats/event/1?session_ids=1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        speaker = SpeakerFactory()
        db.session.add(speaker)
        db.session.commit()


# ------------------------- Events -------------------------
@hooks.before("Events > Events Collection > List All Events")
def event_get_list(transaction):
    """
    GET /events
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before("Events > Events Collection > Create Event")
def event_post(transaction):
    """
    POST /events
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        RoleFactory(
            name=Role.OWNER
        )  # TODO: Change to get_or_create in event after_created
        db.session.commit()


@hooks.before("Events > Upcoming Events Collection > List All Upcoming Events")
def upcoming_event_get_list(transaction):
    """
    GET /events/upcoming
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic(state="published")
        db.session.add(event)
        db.session.commit()


@hooks.before("Events > Event Details > Event Details")
def event_get_detail(transaction):
    """
    GET /events/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before("Events > Event Details > Update Event")
def event_patch(transaction):
    """
    PATCH /events/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before("Events > Event Details > Delete Event")
def event_delete(transaction):
    """
    DELETE /events/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before("Events > Events of an Event Type > List All Events of an Event Type")
def evnt_type_event_get_list(transaction):
    """
    GET /event-types/1/events
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_type = EventTypeFactory()
        db.session.add(event_type)

        event = EventFactoryBasic(event_type_id=1)
        db.session.add(event)
        db.session.commit()


@hooks.before(
    "Events > Events under an Event Topic > List All Events under an Event Topic"
)
def evnt_topic_event_get_list(transaction):
    """
    GET /event-topics/1/events
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_topic = EventTopicFactory()
        db.session.add(event_topic)

        event = EventFactoryBasic(event_topic_id=1)
        db.session.add(event)
        db.session.commit()


@hooks.before(
    "Events > Events under an Event Sub-topic > List All Events under an Event Sub-topic"
)
def evnt_sub_topic_event_get_list(transaction):
    """
    GET /event-sub-topics/1/events
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_sub_topic = EventSubTopicFactory()
        db.session.add(event_sub_topic)

        event = EventFactoryBasic(event_sub_topic_id=1)
        db.session.add(event)
        db.session.commit()


@hooks.before("Events > Events under a User > List All Events under a User")
def user_event_get_list(transaction):
    """
    GET /users/1/events
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before("Events > Events for a Discount Code > List All Events for a Discount Code")
def discount_code_event_get_list(transaction):
    """
    GET /discount-codes/1/events
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()

        discount_code = DiscountCodeFactory(event_id=1)
        db.session.add(discount_code)
        db.session.commit()


@hooks.before("Events > Events under a Group > List All Events under a Group")
def group_event_get_list(transaction):
    """
    GET /groups/1/events
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        EventFactoryBasic()
        group = GroupFactory()
        db.session.add(group)
        db.session.commit()


@hooks.before("Events > Get Event for a Ticket > Event Details for a Ticket")
def event_ticket(transaction):
    """
    GET /tickets/1/event
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)

        ticket = TicketFactory()
        db.session.add(ticket)
        db.session.commit()


@hooks.before(
    "Events > Get Event for a Microlocation > Event Details for a Microlocation"
)
def event_microlocation(transaction):
    """
    GET /microlocations/1/event
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        microlocation = MicrolocationFactory()
        db.session.add(microlocation)
        db.session.commit()


@hooks.before("Events > Get Event for a Social Link > Event Details for a Social Link")
def event_social_link(transaction):
    """
    GET /social-links/1/event
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        social_link = SocialLinkFactory()
        db.session.add(social_link)
        db.session.commit()


@hooks.before("Events > Get Event for a Sponsor > Event Details for a Sponsor")
def event_sponsor(transaction):
    """
    GET /sponsors/1/event
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        sponsor = SponsorFactory()
        db.session.add(sponsor)
        db.session.commit()


@hooks.before(
    "Events > Get Event for a Speakers Call > Event Details for a Speakers Call"
)
def event_speakers_call(transaction):
    """
    GET /speakers-calls/1/event
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        speakers_call = SpeakersCallFactory()
        db.session.add(speakers_call)
        db.session.commit()


@hooks.before("Events > Get Event for a Track > Event Details for a Track")
def event_track(transaction):
    """
    GET /tracks/1/event
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        track = TrackFactory()
        db.session.add(track)
        db.session.commit()


@hooks.before("Events > Get Event for a Session Type > Event Details for a Session Type")
def event_session_types(transaction):
    """
    GET /session-types/1/event
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)

        session_type = SessionTypeFactory()
        db.session.add(session_type)
        db.session.commit()


@hooks.before(
    "Events > Get Event for an Event Copyright > Event Details for an Event Copyright"
)
def event_event_copyright(transaction):
    """
    GET /event-copyrights/1/event
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)

        event_copyright = EventCopyrightFactory()
        db.session.add(event_copyright)
        db.session.commit()


@hooks.before("Events > Get Event for a Tax > Event Details for a Tax")
def event_tax(transaction):
    """
    GET /tax/1/event
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)

        tax = TaxFactory()
        db.session.add(tax)
        db.session.commit()


@hooks.before(
    "Events > Get Event for an Event Invoice > Event Details for an Event Invoice"
)
def event_event_invoice(transaction):
    """
    GET /event-invoices/1/event
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_invoice = EventInvoiceFactory()
        db.session.add(event_invoice)
        db.session.commit()


@hooks.before(
    "Events > Get Event for a Discount Code > Event Details for a Discount Code"
)
def event_discount_code(transaction):
    """
    GET /discount-codes/1/event
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)

        discount_code = DiscountCodeFactory(event_id=1)
        db.session.add(discount_code)
        db.session.commit()


@hooks.before("Events > Get Event for a Session > Event Details for a Session")
def event_sessions(transaction):
    """
    GET /sessions/1/event
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        session = SessionFactory()
        db.session.add(session)
        db.session.commit()


@hooks.before("Events > Get Event for a Ticket Tag > Event Details for a Ticket Tag")
def event_ticket_tag(transaction):
    """
    GET /ticket-tags/1/event
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        ticket_tag = TicketTagFactory()
        db.session.add(ticket_tag)
        db.session.commit()


@hooks.before("Events > Get Event for a Role Invite > Event Details for a Role Invite")
def event_role_invite(transaction):
    """
    GET /role-invites/1/event
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)

        role_invite = RoleInviteFactory()
        db.session.add(role_invite)
        db.session.commit()


@hooks.before("Events > Get Event for a Speaker > Event Details for a Speaker")
def event_speaker(transaction):
    """
    GET /speakers/1/event
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        speaker = SpeakerFactory()
        db.session.add(speaker)
        db.session.commit()


@hooks.before(
    "Events > Get Event for an Email Notification > Event Details for an Email Notification"
)
def event_email_notification(transaction):
    """
    GET /email-notifications/1/event
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        email_notification = EmailNotificationFactory()
        db.session.add(email_notification)
        db.session.commit()


@hooks.before("Events > Get Event for an Attendee > Event Details for an Attendee")
def event_attendee(transaction):
    """
    GET /attendees/1/event
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        attendee = AttendeeFactory()
        db.session.add(attendee)
        db.session.commit()


@hooks.before("Events > Get Event for a Custom Form > Event Details for a Custom Form")
def event_custom_form(transaction):
    """
    GET /custom-forms/1/event
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        custom_form = CustomFormFactory()
        db.session.add(custom_form)
        db.session.commit()


@hooks.before("Events > Get Event for a FAQ > Event Details for a FAQ")
def event_faq(transaction):
    """
    GET /faqs/1/event
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        faq = FaqFactory()
        db.session.add(faq)
        db.session.commit()


@hooks.before(
    "Events > Get Event for a Stripe Authorization > Event Details for a Stripe Authorization"
)
def event_stripe_authorization(transaction):
    """
    GET /stripe-authorization/1/event
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        stripe_authorization = StripeAuthorizationFactory()
        db.session.add(stripe_authorization)
        db.session.commit()


# ------------------------- Group -------------------------
@hooks.before("Group > Group Collection > List All Groups")
def group_get_list(transaction):
    """
    GET /groups
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        EventFactoryBasic()
        group = GroupFactory()
        db.session.add(group)
        db.session.commit()


@hooks.before("Group > Groups under an User > List All Groups under an User")
def group_get_list_from_user(transaction):
    """
    GET /users/1/groups
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        EventFactoryBasic()
        group = GroupFactory()
        db.session.add(group)
        db.session.commit()


@hooks.before("Group > Group Collection > Create Group")
def group_post(transaction):
    """
    POST /groups
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        EventFactoryBasic()
        group = GroupFactory()
        db.session.add(group)
        db.session.commit()


@hooks.before("Group > Group Detail > Group Detail")
def group_get_detail(transaction):
    """
    GET /groups/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        EventFactoryBasic()
        group = GroupFactory()
        db.session.add(group)
        db.session.commit()


@hooks.before("Group > Get Group for an Event > Group Details for an Event")
def group_get_detail_event(transaction):
    """
    GET /events/1/group
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        group = GroupFactory()
        db.session.add(group)
        db.session.commit()

        event = EventFactoryBasic(group_id=1)
        db.session.add(event)
        db.session.commit()


@hooks.before("Group > Group Detail > Update Group")
def group_patch(transaction):
    """
    PATCH /groups/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        EventFactoryBasic()
        group = GroupFactory()
        db.session.add(group)
        db.session.commit()


@hooks.before("Group > Group Detail > Delete Group")
def group_delete(transaction):
    """
    DELETE /groups/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        EventFactoryBasic()
        group = GroupFactory()
        db.session.add(group)
        db.session.commit()


# ------------------------- Feedback -------------------------
@hooks.before("Feedback > Feedback Collection > Create Feedback")
def feedback_post(transaction):
    """
    POST /feedbacks
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        session = SessionFactory()
        db.session.add(session)
        db.session.commit()


@hooks.before("Feedback > Feedback Detail > Feedback Detail")
def feedback_get_detail(transaction):
    """
    GET /feedbacks/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        feedback = FeedbackFactory()
        db.session.add(feedback)
        db.session.commit()


@hooks.before("Feedback > Feedback Detail > Update Feedback")
def feedback_patch(transaction):
    """
    PATCH /feedbacks/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        feedback = FeedbackFactory()
        db.session.add(feedback)
        db.session.commit()


@hooks.before("Feedback > Feedback Detail > Delete Feedback")
def feedback_delete(transaction):
    """
    DELETE /feedbacks/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        feedback = FeedbackFactory()
        db.session.add(feedback)
        db.session.commit()


@hooks.before("Feedback > Event Feedback Collection > List All Feedbacks for an Event")
def feedback_get_list(transaction):
    """
    GET /events/1/Feedbacks
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        feedback = FeedbackFactory()
        db.session.add(feedback)
        db.session.commit()


# ------------------------- Copyright -------------------------
@hooks.before("Copyright > Event Copyright > Create Event Copyright")
def copyright_post(transaction):
    """
    POST /event-copyrights
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before("Copyright > Event Copyright Details > Event Copyright Details")
def copyright_get_detail(transaction):
    """
    GET /event-copyrights/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        copyright = EventCopyrightFactory()
        db.session.add(copyright)
        db.session.commit()


@hooks.before("Copyright > Event Copyright Details > Update Event Copyright")
def copyright_patch(transaction):
    """
    PATCH /event-copyrights/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        copyright = EventCopyrightFactory()
        db.session.add(copyright)
        db.session.commit()


@hooks.before("Copyright > Event Copyright Details > Delete Event Copyright")
def copyright_delete(transaction):
    """
    DELETE /event-copyrights/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        copyright = EventCopyrightFactory()
        db.session.add(copyright)
        db.session.commit()


@hooks.before("Copyright > Get Event Copyright for an Event > Event Copyright Details")
def event_copyright(transaction):
    """
    GET /events/1/event-copyright
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        copyright = EventCopyrightFactory()
        db.session.add(copyright)
        db.session.commit()


# ------------------------- Invoices -------------------------
@hooks.before("Invoices > Event Invoices > Get Event Invoices")
def invoice_get_list(transaction):
    """
    GET /event-invoices
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_invoice = EventInvoiceFactory()
        db.session.add(event_invoice)
        db.session.commit()


@hooks.before("Invoices > Event Invoices Details > Event Invoices Details")
def invoice_get_detail(transaction):
    """
    GET /event-invoices/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_invoice = EventInvoiceFactory()
        db.session.add(event_invoice)
        db.session.commit()


@hooks.before("Invoices > Event Invoices Details > Update Event Invoices")
def invoice_patch(transaction):
    """
    PATCH /event-invoices/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_invoice = EventInvoiceFactory()
        db.session.add(event_invoice)
        db.session.commit()


@hooks.before("Invoices > Event Invoices Details > Delete Event Invoices")
def invoice_delete(transaction):
    """
    DELETE /event-invoices/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_invoice = EventInvoiceFactory()
        db.session.add(event_invoice)
        db.session.commit()


@hooks.before(
    "Invoices > Event Invoice List of an Event > List Event Invoices of an Event"
)
def event_event_invoice_get_list(transaction):
    """
    GET /events/1/event-invoices
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_invoice = EventInvoiceFactory()
        db.session.add(event_invoice)
        db.session.commit()


@hooks.before("Invoices > Event Invoice List of a User > List Event Invoices of a User")
def user_event_invoice_get_list(transaction):
    """
    GET /users/1/event-invoices
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_invoice = EventInvoiceFactory()
        db.session.add(event_invoice)
        db.session.commit()


# ------------------------- Microlocation -------------------------
@hooks.before("Microlocations > Microlocation Collection > Create Microlocation")
def microlocation_post(transaction):
    """
    POST /events/1/microlocations
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before("Microlocations > Microlocation Details > Microlocation Details")
def microlation_get_detail(transaction):
    """
    GET /microlocations/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        microlocation = MicrolocationFactory()
        db.session.add(microlocation)
        db.session.commit()


@hooks.before("Microlocations > Microlocation Details > Update Microlocation")
def microlocation_patch(transaction):
    """
    PATCH /microlocations/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        microlocation = MicrolocationFactory()
        db.session.add(microlocation)
        db.session.commit()


@hooks.before("Microlocations > Microlocation Details > Delete Microlocation")
def microlocation_delete(transaction):
    """
    DELETE /microlocations/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        microlocation = MicrolocationFactory()
        db.session.add(microlocation)
        db.session.commit()


@hooks.before(
    "Microlocations > Microlocations under an Event > Get List of Microlocations under an Event"
)
def event_microlocation_get_list(transaction):
    """
    GET /events/1/microlocations
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        microlocation = MicrolocationFactory()
        db.session.add(microlocation)
        db.session.commit()


@hooks.before(
    "Microlocations > Microlocation Details of a Session > Get Microlocation Details of a Session"
)
def session_microlocation_get_detail(transaction):
    """
    GET /sessions/1/microlocation
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        session = SessionFactory()
        db.session.add(session)
        db.session.commit()


# ------------------------- Sessions -------------------------
@hooks.before("Sessions > Sessions Collection > Create Sessions")
def session_post(transaction):
    """
    POST /events/1/sessions
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        session = SessionFactory()
        db.session.add(session)
        db.session.commit()


@hooks.before("Sessions > Sessions Details > Session Details")
def session_get_detail(transaction):
    """
    GET /sessions/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        session = SessionFactory()
        db.session.add(session)
        db.session.commit()


@hooks.before("Sessions > Sessions Details > Update Session")
def session_patch(transaction):
    """
    PATCH /sessions/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        session = SessionFactory()
        speakers_call = SpeakersCallFactory()
        db.session.add(speakers_call)
        db.session.add(session)
        db.session.commit()


@hooks.before("Sessions > Sessions Details > Delete Session")
def session_delete(transaction):
    """
    DELETE /sessions/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        session = SessionFactory()
        speakers_call = SpeakersCallFactory()
        db.session.add(speakers_call)
        db.session.add(session)
        db.session.commit()


@hooks.before("Sessions > List Sessions under an Event > List Sessions under an Event")
def event_session(transaction):
    """
    GET /events/1/sessions
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        session = SessionFactory()
        db.session.add(session)
        db.session.commit()


@hooks.before("Sessions > List Sessions under a Track > List Sessions under a Track")
def track_session(transaction):
    """
    GET /tracks/1/sessions
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        session = SessionFactory()
        db.session.add(session)
        db.session.commit()


@hooks.before(
    "Sessions > List Sessions under a Session Type > List Sessions under a Session Type"
)
def session_type_session(transaction):
    """
    GET /session-types/1/sessions
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        session = SessionFactory()
        db.session.add(session)
        db.session.commit()


@hooks.before(
    "Sessions > List Sessions under a Microlocation > List Sessions under a Microlocation"
)
def microlocation_session(transaction):
    """
    GET /microlations/1/sessions
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        session = SessionFactory()
        db.session.add(session)
        db.session.commit()


@hooks.before("Sessions > List Sessions under a Speaker > List Sessions under a Speaker")
def speaker_session(transaction):
    """
    GET /speakers/1/sessions
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        speaker = SpeakerFactory()
        db.session.add(speaker)
        db.session.commit()


# ------------------------- Session Type -------------------------
@hooks.before("Session Type > Session Type Collection > Create Session Type")
def session_type_post(transaction):
    """
    POST /session-types
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        session_type = SessionTypeFactory()
        db.session.add(session_type)
        db.session.commit()


@hooks.before("Session Type > Session Type Details > Session Type Details")
def session_type_get_detail(transaction):
    """
    GET /session-types/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        session_type = SessionTypeFactory()
        db.session.add(session_type)
        db.session.commit()


@hooks.before("Session Type > Session Type Details > Update Session Type")
def session_type_patch(transaction):
    """
    PATCH /session-types/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        session_type = SessionTypeFactory()
        db.session.add(session_type)
        db.session.commit()


@hooks.before("Session Type > Session Type Details > Delete Session Type")
def session_type_delete(transaction):
    """
    DELETE /session-types/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        session_type = SessionTypeFactory()
        db.session.add(session_type)
        db.session.commit()


@hooks.before("Session Type > List Session Types under an Event > List Session Types")
def event_session_type(transaction):
    """
    GET /events/1/session-types
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        session_type = SessionTypeFactory()
        db.session.add(session_type)
        db.session.commit()


@hooks.before("Session Type > Get Session Type of a Session > Get Session Type Details")
def session_session_type(transaction):
    """
    GET /sessions/1/session-type
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        session = SessionFactory()
        db.session.add(session)
        db.session.commit()


# ------------------------- Speakers -------------------------
@hooks.before("Speakers > Speakers Collection > Create Speaker")
def speaker_post(transaction):
    """
    POST /speakers
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        speaker = SpeakerFactory()
        db.session.add(speaker)
        db.session.commit()


@hooks.before("Speakers > Speaker Details > Speaker Details")
def speaker_get_detail(transaction):
    """
    GET /speakers/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        speaker = SpeakerFactory()
        db.session.add(speaker)
        db.session.commit()


@hooks.before("Speakers > Speaker Details > Update Speaker")
def speaker_patch(transaction):
    """
    PATCH /speakers/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        speaker = SpeakerFactory()
        speakers_call = SpeakersCallFactory()
        db.session.add(speakers_call)
        db.session.add(speaker)
        db.session.commit()


@hooks.before("Speakers > Speaker Details > Delete Speaker")
def speaker_delete(transaction):
    """
    DELETE /speakers/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        speaker = SpeakerFactory()
        speakers_call = SpeakersCallFactory()
        db.session.add(speakers_call)
        db.session.add(speaker)
        db.session.commit()


@hooks.before("Speakers > List Speakers under an Event > List Speakers under an Event")
def event_speakers(transaction):
    """
    GET /events/1/speakers
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        speaker = SpeakerFactory()
        db.session.add(speaker)
        db.session.commit()


@hooks.before("Speakers > List Speakers under a Session > List Speakers under a Session")
def sessions_speakers(transaction):
    """
    GET /sessions/1/speakers
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        speaker = SpeakerFactory()
        db.session.add(speaker)
        db.session.commit()


@hooks.before(
    "Speakers > List Speaker Profiles for a User > List Speaker Profiles for a User"
)
def user_speakers(transaction):
    """
    GET /users/1/speakers
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        speaker = SpeakerFactory()
        db.session.add(speaker)
        db.session.commit()


# ------------------------- Social Links -------------------------
@hooks.before(
    "Social Links > Social Links Get Collection > List All Social Links under an Event"
)
def social_link_get_list(transaction):
    """
    GET /events/1/social-links
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        social_link = SocialLinkFactory()
        db.session.add(social_link)
        db.session.commit()


@hooks.before("Social Links > Social Links Post Collection > Create Social Link")
def social_link_post(transaction):
    """
    POST /events/1/social-links
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        social_link = SocialLinkFactory()
        db.session.add(social_link)
        db.session.commit()


@hooks.before("Social Links > Social Links > Social Link Detail")
def social_link_get_detail(transaction):
    """
    GET /social-links/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        social_link = SocialLinkFactory()
        db.session.add(social_link)
        db.session.commit()


@hooks.before("Social Links > Social Links > Update Social Link")
def social_link_patch(transaction):
    """
    PATCH /social-links/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        social_link = SocialLinkFactory()
        db.session.add(social_link)
        db.session.commit()


@hooks.before("Social Links > Social Links > Delete Social Link")
def social_link_delete(transaction):
    """
    DELETE /social-links/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        social_link = SocialLinkFactory()
        db.session.add(social_link)
        db.session.commit()


# ------------------------- Speakers Calls -------------------------


@hooks.before("Speakers Calls > Speakers Call Collection > Create Speakers Call")
def speakers_call_post(transaction):
    """
    POST /speakers-calls
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Speakers Calls > Speakers Call Details > Speakers Call Details")
def speakers_call_get_detail(transaction):
    """
    GET /speakers-calls/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        speakers_call = SpeakersCallFactory()
        db.session.add(speakers_call)
        db.session.commit()


@hooks.before("Speakers Calls > Speakers Call Details > Update Speakers Call")
def speakers_call_patch(transaction):
    """
    PATCH /speakers-calls/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        speakers_call = SpeakersCallFactory()
        db.session.add(speakers_call)
        db.session.commit()


@hooks.before("Speakers Calls > Speakers Call Details > Delete Speakers Call")
def speakers_call_delete(transaction):
    """
    DELETE /speakers-calls/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        speakers_call = SpeakersCallFactory()
        db.session.add(speakers_call)
        db.session.commit()


@hooks.before(
    "Speakers Calls > Get Speakers Call for an Event > Get Speakers Call Details for an Event"
)
def speakers_call_event(transaction):
    """
    GET /events/1/speakers-call
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        speakers_call = SpeakersCallFactory()
        db.session.add(speakers_call)
        db.session.commit()


# ------------------------- Sponsors -------------------------
@hooks.before("Sponsors > Sponsors Get Collection > List All Sponsors")
def sponsor_get_list(transaction):
    """
    GET /events/1/sponsors
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        sponsor = SponsorFactory()
        db.session.add(sponsor)
        db.session.commit()


@hooks.before("Sponsors > Sponsors Post Collection > Create Sponsor")
def sponsor_post(transaction):
    """
    POST /sponsors
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        sponsor = SponsorFactory()
        db.session.add(sponsor)
        db.session.commit()


@hooks.before("Sponsors > Sponsor Details > Sponsor Details")
def sponsor_get_detail(transaction):
    """
    GET /sponsors/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        sponsor = SponsorFactory()
        db.session.add(sponsor)
        db.session.commit()


@hooks.before("Sponsors > Sponsor Details > Update Sponsor")
def sponsor_patch(transaction):
    """
    PATCH /sponsors/1
    :param transaction:
    :return:
    """

    with stash['app'].app_context():
        sponsor = SponsorFactory()
        db.session.add(sponsor)
        db.session.commit()


@hooks.before("Sponsors > Sponsor Details > Delete Sponsor")
def sponsor_delete(transaction):
    """
    DELETE /sponsors/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        sponsor = SponsorFactory()
        db.session.add(sponsor)
        db.session.commit()


# ------------------------- Tax -------------------------
@hooks.before("Tax > Tax Collection > Create Tax")
def tax_post(transaction):
    """
    POST /taxes
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before("Tax > Tax Details > Tax Details")
def tax_get_detail(transaction):
    """
    GET /taxes/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        tax = TaxFactory()
        db.session.add(tax)
        db.session.commit()


@hooks.before("Tax > Tax Details > Update Tax")
def tax_patch(transaction):
    """
    PATCH /taxes/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        tax = TaxFactory()
        db.session.add(tax)
        db.session.commit()


@hooks.before("Tax > Tax Details > Delete Tax")
def tax_delete(transaction):
    """
    DELETE /taxes/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        tax = TaxFactory()
        db.session.add(tax)
        db.session.commit()


@hooks.before("Tax > Get Tax details under an Event > Get Tax details under an Event")
def event_tax_get_list(transaction):
    """
    GET /taxes/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        tax = TaxFactory()
        db.session.add(tax)
        db.session.commit()


# ------------------------- Tickets -------------------------
@hooks.before("Tickets > Tickets Collection > Create Ticket")
def ticket_post(transaction):
    """
    POST /tickets
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        ticket = TicketFactory()
        db.session.add(ticket)
        db.session.commit()


@hooks.before("Tickets > Ticket Details > Ticket Details")
def ticket_get_detail(transaction):
    """
    GET /tickets/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        ticket = TicketFactory()
        db.session.add(ticket)
        db.session.commit()


@hooks.before("Tickets > Ticket Details > Update Ticket")
def ticket_patch(transaction):
    """
    PATCH /tickets/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        ticket = TicketFactory()
        db.session.add(ticket)
        db.session.commit()


@hooks.before("Tickets > Ticket Details > Delete Ticket")
def ticket_delete(transaction):
    """
    DELETE /tickets/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        ticket = TicketFactory()
        db.session.add(ticket)
        db.session.commit()


@hooks.before("Tickets > List Tickets under an Event > List Tickets under an Event")
def ticket_event(transaction):
    """
    GET /events/1/tickets
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before(
    "Tickets > List Tickets under a Ticket-tag > List Tickets under a Ticket-tag"
)
def tikcet_tag_ticket(transaction):
    """
    GET /tikcet-tags/1/tickets
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        ticket_tag = TicketTagFactory()
        db.session.add(ticket_tag)
        db.session.commit()


@hooks.before(
    "Tickets > List Tickets for an Access Code > List Tickets for an Access Code"
)
def access_code_ticket(transaction):
    """
    GET /access-codes/1/tickets
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        access_code = AccessCodeFactory()
        db.session.add(access_code)
        db.session.commit()


@hooks.before(
    "Tickets > List Tickets for a Discount Code > List Tickets for a Discount Code"
)
def discount_code_ticket(transaction):
    """
    GET /discount-codes/1/tickets
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        discount_code = DiscountCodeTicketFactory(event_id=1)
        db.session.add(discount_code)
        db.session.commit()


@hooks.before("Tickets > List Tickets for an Order > List Tickets for an Order")
def get_tickets_from_order(transaction):
    """
    GET /v1/orders/{identifier}/tickets
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        order = OrderFactory()
        order.identifier = "7201904e"
        db.session.add(order)
        db.session.commit()


# ------------------------- Ticket Fees -------------------------
@hooks.before("Ticket Fees > Ticket Fees Collection > List Ticket Fees")
def ticket_fees_get_list(transaction):
    """
    GET /ticket-fees
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        ticket_fees = TicketFeesFactory()
        db.session.add(ticket_fees)
        db.session.commit()


@hooks.before("Ticket Fees > Ticket Fees Collection > Create Ticket Fee")
def ticket_fees_post(transaction):
    """
    POST /ticket-fees
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        ticket_fees = TicketFeesFactory()
        db.session.add(ticket_fees)
        db.session.commit()


@hooks.before("Ticket Fees > Ticket Fee Details > Get Ticket Fees Details")
def ticket_fees_get_detail(transaction):
    """
    GET /ticket-fees/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        ticket_fees = TicketFeesFactory()
        db.session.add(ticket_fees)
        db.session.commit()


@hooks.before("Ticket Fees > Ticket Fee Details > Update Ticket Fees")
def ticket_fees_patch(transaction):
    """
    PATCH /ticket-fees/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        ticket_fees = TicketFeesFactory()
        db.session.add(ticket_fees)
        db.session.commit()


@hooks.before("Ticket Fees > Ticket Fee Details > Delete Ticket Fees")
def ticket_fees_delete(transaction):
    """
    DELETE /ticket-fees/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        ticket_fees = TicketFeesFactory()
        db.session.add(ticket_fees)
        db.session.commit()


# ------------------------- Ticket Tags -------------------------
@hooks.before("Ticket Tags > Ticket Tags Collection > Create Ticket Tag")
def ticket_tag_post(transaction):
    """
    POST /ticket-tags
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        ticket_tag = TicketTagFactory()
        db.session.add(ticket_tag)
        db.session.commit()


@hooks.before("Ticket Tags > Ticket Tag Details > Ticket Tag Details")
def ticket_tag_get_detail(transaction):
    """
    GET /ticket-tags/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        ticket_tag = TicketTagFactory()
        db.session.add(ticket_tag)
        db.session.commit()


@hooks.before("Ticket Tags > Ticket Tag Details > Update Ticket Tag")
def ticket_tag_patch(transaction):
    """
    PATCH /ticket-tags/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        ticket_tag = TicketTagFactory()
        db.session.add(ticket_tag)
        db.session.commit()


@hooks.before("Ticket Tags > Ticket Tag Details > Delete Ticket Tag")
def ticket_tag_delete(transaction):
    """
    DELETE /ticket-tags/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        ticket_tag = TicketTagFactory()
        db.session.add(ticket_tag)
        db.session.commit()


@hooks.before(
    "Ticket Tags > List Ticket Tags under an Event > List Ticket Tags under an Event"
)
def ticket_tag_event(transaction):
    """
    GET /events/1/ticket-tags
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before(
    "Ticket Tags > List Ticket Tags for a Ticket > List Ticket Tags for a Ticket"
)
def ticket_tag_ticket(transaction):
    """
    GET /tickets/1/ticket-tags
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        ticket = TicketFactory()
        db.session.add(ticket)
        db.session.commit()


# ---------------------- Attendees (Ticket Holder) ---------------------
@hooks.before("Attendees > Attendees Collection > Create Attendee")
def attendee_post(transaction):
    """
    POST /attendees
    :param transaction:
    :return:
    """
    # Skip until docs for direct endpoints added
    with stash['app'].app_context():
        ticket = TicketFactory()
        db.session.add(ticket)

        attendee = AttendeeFactory(ticket_id=1)
        db.session.add(attendee)
        db.session.commit()


@hooks.before("Attendees > Attendee Details > Attendee Details")
def attendee_get_detail(transaction):
    """
    GET /attendees/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        attendee = AttendeeFactory()
        db.session.add(attendee)
        db.session.commit()


@hooks.before("Attendees > Attendee Details > Update Attendee")
def attendee_patch(transaction):
    """
    PATCH /attendees/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        attendee = AttendeeOrderSubFactory()
        db.session.add(attendee)
        db.session.commit()


@hooks.before("Attendees > Attendee Details > Delete Attendee")
def attendee_delete(transaction):
    """
    DELETE /attendees/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        attendee = AttendeeOrderSubFactory()
        db.session.add(attendee)
        db.session.commit()


@hooks.before("Attendees > Send order receipts > Send email receipts to attendees")
def attendee_receipts(transaction):
    """
    POST /attendees/send-receipt
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        order = OrderFactory()
        order.identifier = 'xyz789'
        order.status = 'completed'
        db.session.add(order)
        db.session.commit()


@hooks.before(
    "Attendees > List Attendees under an order > List All Attendees under an order"
)
def get_attendees_from_order(transaction):
    """
    GET /v1/orders/{identifier}/attendees
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        order = OrderFactory()
        order.identifier = "7201904e"
        db.session.add(order)
        db.session.commit()


@hooks.before(
    "Attendees > List Attendees under an event > List All Attendees under an event"
)
def get_attendees_from_event(transaction):
    """
    GET /v1/events/{event_id}/attendees
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before(
    "Attendees > List Attendees under a ticket > List All Attendees under a ticket"
)
def get_attendees_from_ticket(transaction):
    """
    GET /v1/tickets/{ticket_id}/attendees
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        ticket = TicketFactory()
        db.session.add(ticket)
        db.session.commit()


@hooks.before("Attendees > Get Attendee State > Get Attendee State")
def get_attendee_state(transaction):
    """
    GET /v1/states{?event_id,attendee_id}
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        microlocation = MicrolocationSubFactory(
            event=event,
        )
        ticket = TicketSubFactory(
            event=event,
        )
        StationSubFactory(
            event=event, microlocation=microlocation, station_type='registration'
        )
        SessionSubFactory(
            event=event,
            microlocation=microlocation,
        )
        AttendeeSubFactory(
            event=event,
            ticket=ticket,
        )
        db.session.commit()


# ------------------------- Tracks -------------------------
@hooks.before("Tracks > Tracks Collection > Create Track")
def track_post(transaction):
    """
    POST /events/1/tracks
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        track = TrackFactory()
        db.session.add(track)
        db.session.commit()


@hooks.before("Tracks > Track Detail > Get Details")
def track_get_detail(transaction):
    """
    GET /tracks/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        track = TrackFactory()
        db.session.add(track)
        db.session.commit()


@hooks.before("Tracks > Track Detail > Update Track")
def track_patch(transaction):
    """
    GET /tracks/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        track = TrackFactory()
        db.session.add(track)
        db.session.commit()


@hooks.before("Tracks > Track Detail > Delete Track")
def track_delete(transaction):
    """
    DELETE /tracks/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        track = TrackFactory()
        db.session.add(track)
        db.session.commit()


@hooks.before("Tracks > Tracks under an Event > Get List of Tracks under an Event")
def event_track_get_list(transaction):
    """
    GET /events/1/tracks
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before("Tracks > Tracks Details of a Session > Get Track Details of a Session")
def session_track_get_detail(transaction):
    """
    GET /sessions/1/track
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        session = SessionFactory()
        db.session.add(session)
        db.session.commit()


# ------------------------- Notifications -------------------------
@hooks.before("Notifications > Notifications Collection > List All Notifications")
def notification_get_list(transaction):
    """
    GET /users/2/notifications
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        NotificationSubFactory()
        db.session.commit()


@hooks.before("Notifications > Notifications Admin Collection > List All Notifications")
def notification_get_admin_list(transaction):
    """
    GET /notifications
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        NotificationSubFactory()
        db.session.commit()


@hooks.before("Notifications > Notification Detail > Notification Detail")
def notification_get_detail(transaction):
    """
    GET /notifications/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        NotificationSubFactory()
        db.session.commit()


@hooks.before(
    "Notifications > Notification Detail with Actions > Notification Detail with Actions"
)
def notification_get_detail_with_actions(transaction):
    """
    GET /notifications/1?include=notification_actions
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        NotificationSubFactory()
        db.session.commit()


@hooks.before("Notifications > Notification Detail > Update Notification")
def notification_patch(transaction):
    """
    PATCH /notifications/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        NotificationSubFactory()
        db.session.commit()


@hooks.before("Notifications > Notification Detail > Delete Notification")
def notification_delete(transaction):
    """
    DELETE /notifications/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        NotificationSubFactory()
        db.session.commit()


# ------------------------- Email Notifications -------------------------
@hooks.before(
    "Email Notifications > Email Notifications Admin Collection > List All Email Notifications"
)
def email_notification_get_admin_list(transaction):
    """
    GET /email-notifications
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        email_notification = EmailNotificationFactory()
        db.session.add(email_notification)
        db.session.commit()


@hooks.before(
    "Email Notifications > Email Notifications Collection > List All Email Notifications"
)
def email_notification_get_list(transaction):
    """
    GET /users/2/email-notifications
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        email_notification = EmailNotificationFactory()
        db.session.add(email_notification)
        db.session.commit()


@hooks.before(
    "Email Notifications > Email Notifications Collection Post > Create Email Notificaiton"
)
def email_notification_post(transaction):
    """
    POST /email-notifications
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        email_notification = EmailNotificationFactory()
        db.session.add(email_notification)
        db.session.commit()


@hooks.before(
    "Email Notifications > Email Notification Detail > Email Notification Detail"
)
def email_notification_get_detail(transaction):
    """
    GET /email-notifications/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        email_notification = EmailNotificationFactory()
        db.session.add(email_notification)
        db.session.commit()


@hooks.before(
    "Email Notifications > Email Notification Detail > Update Email Notification"
)
def email_notification_patch(transaction):
    """
    PATCH /email-notifications/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        email_notification = EmailNotificationFactory()
        db.session.add(email_notification)
        db.session.commit()


@hooks.before(
    "Email Notifications > Email Notification Detail > Delete Email Notification"
)
def email_notification_delete(transaction):
    """
    DELETE /email-notifications/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        email_notification = EmailNotificationFactory()
        db.session.add(email_notification)
        db.session.commit()


# ------------------------- User Emails -------------------------
@hooks.before("User Emails > User Email Admin Collection > List All User Emails")
def user_email_get_admin_list(transaction):
    """
    GET /admin/user-emails
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        user_email = UserEmailFactory()
        db.session.add(user_email)
        db.session.commit()


@hooks.before("User Emails > User Email Collection > List All User Emails")
def user_email_get_list(transaction):
    """
    GET /users/2/alternate-emails
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        user_email = UserEmailFactory()
        db.session.add(user_email)
        db.session.commit()


@hooks.before("User Emails > User Email Collection Post > Create User Email")
def user_email_post(transaction):
    """
    POST /user-emails
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        user_email = UserEmailFactory()
        # user = UserFactory()
        # db.session.add(user)
        db.session.add(user_email)
        db.session.commit()


@hooks.before("User Emails > User Email Detail > User Email Detail")
def user_email_get_detail(transaction):
    """
    GET /user-emails/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        user_email = UserEmailFactory()
        db.session.add(user_email)
        db.session.commit()


@hooks.before("User Emails > User Email Detail > Update User Email")
def user_email_patch(transaction):
    """
    PATCH /user-emails/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        user_email = UserEmailFactory()
        db.session.add(user_email)
        db.session.commit()


@hooks.before("User Emails > User Email Detail > Delete User Email")
def user_email_delete(transaction):
    """
    DELETE /user-emails/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        user_email = UserEmailFactory()
        db.session.add(user_email)
        db.session.commit()


# ------------------------- Image Size -------------------------
@hooks.before("Image Size > Event Image Size Details > Get Event Image Size Details")
def event_image_size_get_detail(transaction):
    """
    GET /event-image-sizes
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_image_size = EventImageSizeFactory()
        db.session.add(event_image_size)
        db.session.commit()


@hooks.before("Image Size > Event Image Size Details > Update Event Image Size")
def event_image_size_patch(transaction):
    """
    PATCH /event-image-sizes
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_image_size = EventImageSizeFactory()
        db.session.add(event_image_size)
        db.session.commit()


@hooks.before("Image Size > Speaker Image Size Details > Get Speaker Image Size Details")
def speaker_image_size_get_detail(transaction):
    """
    GET /speaker-image-sizes
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        EventImageSizeFactory()
        SpeakerImageSizeFactory()
        db.session.commit()


@hooks.before("Image Size > Speaker Image Size Details > Update Speaker Image Size")
def speaker_size_patch(transaction):
    """
    PATCH /speaker-image-sizes
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        EventImageSizeFactory()
        SpeakerImageSizeFactory()
        db.session.commit()


# ------------------------- Roles -------------------------
@hooks.before("Roles > Roles Collection > List Roles")
def role_list(transaction):
    """
    GET /roles
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        role = RoleFactory()
        db.session.add(role)
        db.session.commit()


@hooks.before("Roles > Roles Collection > Create Role")
def role_post(transaction):
    """
    POST /roles
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        role = RoleFactory()
        db.session.add(role)
        db.session.commit()


@hooks.before("Roles > Role Details > Get Role Details")
def role_detail(transaction):
    """
    GET /roles/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        role = RoleFactory()
        db.session.add(role)
        db.session.commit()


@hooks.before("Roles > Role Details > Update Role")
def role_patch(transaction):
    """
    PATCH /roles/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        role = RoleFactory()
        db.session.add(role)
        db.session.commit()


@hooks.before("Roles > Role Details > Delete Role")
def role_delete(transaction):
    """
    DELETE /roles/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        role = RoleFactory(name="example role")
        db.session.add(role)
        db.session.commit()


@hooks.before("Roles > Get Role for a Role Invite > Get Role Details for a Role Invite")
def role_role_invite(transaction):
    """
    GET /role-invites/1/role
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        role_invite = RoleInviteFactory()
        db.session.add(role_invite)
        db.session.commit()


# ------------------------- Service -------------------------
@hooks.before("Services > Services Collection > List Services")
def service(transaction):
    """
    GET /services
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        service = ServiceFactory()
        db.session.add(service)
        db.session.commit()


@hooks.before("Services > Services Details > Get Service Details")
def service_detail(transaction):
    """
    GET /services/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        service = ServiceFactory()
        db.session.add(service)
        db.session.commit()


@hooks.before("Services > Services Details > Update Service")
def service_patch(transaction):
    """
    PATCH /services/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        service = ServiceFactory()
        db.session.add(service)
        db.session.commit()


# ------------------------- Event Role Permission -------------------------
@hooks.before(
    "Event Role Permission > Event Role Permission Collection > List Event Role Permissions"
)
def event_role_permission_list(transaction):
    """
    GET /event-role-permissions
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_role_permission = EventRolePermissionsFactory()
        db.session.add(event_role_permission)
        db.session.commit()


@hooks.before(
    "Event Role Permission > Event Role Permission Details > Get Event Role Permission Details"
)
def event_role_permission_detail(transaction):
    """
    GET /event-role-permissions/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_role_permission = EventRolePermissionsFactory()
        db.session.add(event_role_permission)
        db.session.commit()


@hooks.before(
    "Event Role Permission > Event Role Permission Details > Update Event Role Permission"
)
def event_role_permission_patch(transaction):
    """
    PATCH /event-role-permissions/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_role_permission = EventRolePermissionsFactory()
        db.session.add(event_role_permission)
        db.session.commit()


# ------------------------- Message Setting -------------------------
@hooks.before("Message Settings > Message Setting Collection > List Message Settings")
def message_setting_list(transaction):
    """
    GET /message-settings
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        message_setting = MessageSettingsFactory()
        db.session.add(message_setting)
        db.session.commit()


@hooks.before("Message Settings > Message Setting Details > Get Message Setting Details")
def message_setting_detail(transaction):
    """
    GET /message-settings/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        message_setting = MessageSettingsFactory()
        db.session.add(message_setting)
        db.session.commit()


@hooks.before("Message Settings > Message Setting Details > Update Message Setting")
def message_setting_patch(transaction):
    """
    PATCH /message-settings/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        message_setting = MessageSettingsFactory()
        db.session.add(message_setting)
        db.session.commit()


# ------------------------- Activities -------------------------
@hooks.before("Activity > Activity Collection > List all Activities")
def activity_get_list(transaction):
    """
    GET /activities
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        activity = ActivityFactory()
        db.session.add(activity)
        db.session.commit()


@hooks.before("Activity > Activity Details > Get Activity Details")
def activity_get_detail(transaction):
    """
    GET /activities/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        activity = ActivityFactory()
        db.session.add(activity)
        db.session.commit()


# ------------------------- Pages -------------------------
@hooks.before("Pages > Page Collection > Page Sizes")
def page_get_list(transaction):
    """
    GET /pages
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        page = PageFactory()
        db.session.add(page)
        db.session.commit()


@hooks.before("Pages > Page Collection > Create Page")
def page_post(transaction):
    """
    POST /pages
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        page = PageFactory()
        db.session.add(page)
        db.session.commit()


@hooks.before("Pages > Page Details > Get Page Details")
def page_get_detail(transaction):
    """
    GET /pages/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        page = PageFactory()
        db.session.add(page)
        db.session.commit()


@hooks.before("Pages > Page Details > Update Page")
def page_patch(transaction):
    """
    PATCH /pages/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        page = PageFactory()
        db.session.add(page)
        db.session.commit()


@hooks.before("Pages > Page Details > Delete Page")
def page_delete(transaction):
    """
    DELETE /pages/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        page = PageFactory()
        db.session.add(page)
        db.session.commit()


# ------------------------- Mails -------------------------
@hooks.before("Mails > Mail Collection > Show all mails")
def mail_get_list(transaction):
    """
    GET /mails
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        mail = MailFactory()
        db.session.add(mail)
        db.session.commit()


@hooks.before("Mails > Mail Details > Get Mail Details")
def mail_get_detail(transaction):
    """
    GET /mails/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        mail = MailFactory()
        db.session.add(mail)
        db.session.commit()


# ------------------------- Settings -------------------------
@hooks.before("Settings > Settings Details > Show Settings")
def settings_get_list(transaction):
    """
    GET /settings
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        setting = SettingFactory()
        db.session.add(setting)
        db.session.commit()


@hooks.before("Settings > Settings Details > Update Settings")
def settings_patch(transaction):
    """
    PATCH /settings
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        setting = SettingFactory()
        db.session.add(setting)
        db.session.commit()


# ------------------------- Discount Codes -------------------------
@hooks.before(
    "Discount Codes > Event Discount Code Collection > List All Event Discount Codes"
)
def event_discount_code_get_list(transaction):
    """
    GET /discount-codes
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()

        discount_code_event = DiscountCodeFactory(event_id=1)
        db.session.add(discount_code_event)
        discount_code_ticket = DiscountCodeFactory(event_id=1, used_for="ticket")
        db.session.add(discount_code_ticket)
        db.session.commit()


@hooks.before(
    "Discount Codes > Event Discount Code Collection > Create Event Discount Code"
)
def event_discount_code_post(transaction):
    """
    POST /discount-codes
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        EventFactoryBasic()
        db.session.commit()


@hooks.before(
    "Discount Codes > Ticket Discount Code Collection > Create Ticket Discount Code"
)
def ticket_discount_code_post(transaction):
    """
    POST /discount-codes
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        TicketFactory()
        db.session.commit()


@hooks.before(
    "Discount Codes > Ticket Discount Code Collection > List All Ticket Discount Codes"
)
def ticket_discount_code_get_list(transaction):
    """
    GET /events/1/discount-codes
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()

        discount_code = DiscountCodeTicketFactory(event_id=1)
        db.session.add(discount_code)
        db.session.commit()


@hooks.before("Discount Codes > Discount Code Detail > Discount Code Detail")
def discount_code_get_detail(transaction):
    """
    GET /discount-codes/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()

        discount_code = DiscountCodeTicketFactory(event_id=1)
        db.session.add(discount_code)
        db.session.commit()


@hooks.before("Discount Codes > Discount Code Detail > Update Discount Code")
def discount_code_patch(transaction):
    """
    PATCH /discount-codes/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()

        discount_code = DiscountCodeTicketFactory(event_id=1)
        db.session.add(discount_code)
        db.session.commit()


@hooks.before("Discount Codes > Discount Code Detail > Delete Discount Code")
def discount_delete(transaction):
    """
    DELETE /discount-codes/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()

        discount_code = DiscountCodeFactory(event_id=1)
        db.session.add(discount_code)
        db.session.commit()


@hooks.before(
    "Discount Codes > Get Discount Code Detail using the code > Get Discount Code Detail"
)
def discount_code_get_detail_using_code(transaction):
    """
    GET events/1/discount-codes/DC101
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()

        discount_code = DiscountCodeFactory(event_id=1)
        discount_code.code = 'DC101'
        discount_code.event_id = 1
        db.session.add(discount_code)
        db.session.commit()


@hooks.before(
    "Discount Codes > List Discount Codes under a User > List All Discount Codes under a User"
)
def user_discount_code_get_list(transaction):
    """
    GET /users/1/discount-codes
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()

        discount_code = DiscountCodeFactory(event_id=1)
        db.session.add(discount_code)
        db.session.commit()


@hooks.before(
    "Discount Codes > List Discount Codes under a Ticket > List All Discount Codes under a Ticket"
)
def get_discount_codes_under_ticket(transaction):
    """
    GET /tickets/1/discount-codes
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        discount_code = DiscountCodeTicketFactory(event_id=1)
        db.session.add(discount_code)
        db.session.commit()


@hooks.before(
    "Discount Codes > Get Discount Code Detail of an Event > Get Discount Code Detail of an Event"
)
def event_discount_code_get_detail(transaction):
    """
    GET /events/1/discount-code
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        discount_code = DiscountCodeFactory()
        db.session.add(discount_code)
        db.session.commit()

        event = EventFactoryBasic(discount_code_id=1)
        db.session.add(event)
        db.session.commit()


@hooks.before(
    "Discount Codes > Get Discount Code Detail of an Event Invoice > "
    "Get Discount Code Detail of an Event Invoice"
)
def event_invoice_discount_code_get_detail(transaction):
    """
    GET /event-invoices/1/discount-code
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()

        event_invoice = EventInvoiceFactory()
        db.session.add(event_invoice)
        db.session.commit()


# ------------------------- Access Codes -------------------------
@hooks.before("Access Codes > Access Code Collection > Create Access Code")
def access_code_post(transaction):
    """
    POST /access-codes
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        access_code = AccessCodeFactory()
        db.session.add(access_code)
        db.session.commit()


@hooks.before("Access Codes > Access Code Detail > Access Code Detail")
def access_code_get_detail(transaction):
    """
    GET /access-codes/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        access_code = AccessCodeFactory()
        db.session.add(access_code)
        db.session.commit()


@hooks.before("Access Codes > Access Code Detail > Update Access Code")
def access_code_patch(transaction):
    """
    PATCH /access-codes/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        access_code = AccessCodeFactory()
        db.session.add(access_code)
        db.session.commit()


@hooks.before("Access Codes > Access Code Detail > Delete Access Code")
def access_code_delete(transaction):
    """
    DELETE /access-codes/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        access_code = AccessCodeFactory()
        db.session.add(access_code)
        db.session.commit()


@hooks.before("Access Codes > Access Code Detail using the Code > Access Code Detail")
def access_code_get_detail_using_code(transaction):
    """
    GET events/1/access-codes/AC101
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()

        access_code = AccessCodeFactory()
        access_code.code = 'AC101'
        db.session.add(access_code)
        db.session.commit()


@hooks.before(
    "Access Codes > Get Access Codes for an Event > List All Access Codes of an Event"
)
def event_access_code_get_list(transaction):
    """
    GET /events/1/access-codes
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before(
    "Access Codes > Get Access Codes for a User > List All Access Codes for a User"
)
def user_access_code_get_list(transaction):
    """
    GET /users/1/access-codes
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        user = UserFactory()
        db.session.add(user)
        db.session.commit()


@hooks.before(
    "Access Codes > Get Access Codes for a Ticket > List All Access Codes for a Ticket"
)
def ticket_access_code_get_list(transaction):
    """
    GET /tickets/1/access-codes
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        ticket = TicketFactory()
        db.session.add(ticket)
        db.session.commit()


# ------------------------- Custom Forms -------------------------
@hooks.before("Custom Forms > Custom Form Collection > Create Custom Form")
def custom_form_post(transaction):
    """
    POST /custom-forms
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        custom_form = CustomFormFactory()
        db.session.add(custom_form)
        db.session.commit()


@hooks.before("Custom Forms > Custom Form Detail > Custom Form Detail")
def custom_form_get_detail(transaction):
    """
    GET /custom-forms/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        custom_form = CustomFormFactory()
        db.session.add(custom_form)
        db.session.commit()


@hooks.before("Custom Forms > Custom Form Detail > Update Custom Form")
def custom_form_patch(transaction):
    """
    PATCH /custom-forms/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        custom_form = CustomFormFactory()
        db.session.add(custom_form)
        db.session.commit()


@hooks.before("Custom Forms > Custom Form Detail > Delete Custom Form")
def custom_form_delete(transaction):
    """
    DELETE /custom-forms/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        custom_form = CustomFormFactory()
        db.session.add(custom_form)
        db.session.commit()


@hooks.before(
    "Custom Forms > Event Custom Form Collection > List All Custom Forms for an Event"
)
def custom_form_get_list(transaction):
    """
    GET /events/1/custom-forms
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        custom_form = CustomFormFactory()
        db.session.add(custom_form)
        db.session.commit()


# ------------------------- FAQ -------------------------
@hooks.before("FAQ > FAQ Collection > Create FAQ")
def faq_post(transaction):
    """
    POST /faqs
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        faq = FaqFactory()
        db.session.add(faq)
        db.session.commit()


@hooks.before("FAQ > FAQ Detail > FAQ Detail")
def faq_get_detail(transaction):
    """
    GET /faqs/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        faq = FaqFactory()
        db.session.add(faq)
        db.session.commit()


@hooks.before("FAQ > FAQ Detail > Update FAQ")
def faq_patch(transaction):
    """
    PATCH /faqs/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        faq = FaqFactory()
        db.session.add(faq)
        db.session.commit()


@hooks.before("FAQ > FAQ Detail > Delete FAQ")
def faq_delete(transaction):
    """
    DELETE /faqs/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        faq = FaqFactory()
        db.session.add(faq)
        db.session.commit()


@hooks.before("FAQ > Event FAQ Collection > List All FAQs for an Event")
def faq_get_list(transaction):
    """
    GET /events/1/faqs
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


# ------------------------- FAQ Types -------------------------
@hooks.before("FAQ Types > FAQ Type Collection > Create FAQ Type")
def faq_type_post(transaction):
    """
    POST /faq-types
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        faq_type = FaqTypeFactory()
        db.session.add(faq_type)
        db.session.commit()


@hooks.before("FAQ Types > FAQ Type Detail > FAQ Type Detail")
def faq_type_get_detail(transaction):
    """
    GET /faq-types/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        faq_type = FaqTypeFactory()
        db.session.add(faq_type)
        db.session.commit()


@hooks.before("FAQ Types > FAQ Type Detail > Update FAQ Type")
def faq_type_patch(transaction):
    """
    PATCH /faq-types/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        faq_type = FaqTypeFactory()
        db.session.add(faq_type)
        db.session.commit()


@hooks.before("FAQ Types > FAQ Type Detail > Delete FAQ Type")
def faq_type_delete(transaction):
    """
    DELETE /faq-types/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        faq_type = FaqTypeFactory()
        db.session.add(faq_type)
        db.session.commit()


@hooks.before("FAQ Types > Event FAQ Type Collection > List All FAQ Types for an Event")
def event_faq_type_get_list(transaction):
    """
    GET /events/1/faq-types
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before("FAQ Types > FAQ FAQ Type Collection > List All FAQ Types for a FAQ")
def faq_faq_type_get_list(transaction):
    """
    GET /faq/1/faq-types
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        faq = FaqFactory()
        db.session.add(faq)
        db.session.commit()


# ------------------------- Role Invites -------------------------
@hooks.before("Role Invites > Role Invites Collection List > List All Role Invites")
def role_invite_get_list(transaction):
    """
    GET /events/1/role-invites
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        role_invite = RoleInviteFactory()
        db.session.add(role_invite)
        db.session.commit()


@hooks.before("Role Invites > Role Invites Collection > Create Role Invite")
def role_invite_post(transaction):
    """
    POST /role-invites
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        RoleFactory()
        EventFactoryBasic()
        db.session.commit()


@hooks.before("Role Invites > Role Invite Details > Role Invite Details")
def role_invite_get_detail(transaction):
    """
    GET /role-invites/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        role_invite = RoleInviteFactory()
        db.session.add(role_invite)
        db.session.commit()


@hooks.before(
    "Role Invites > User Email Details By Role Invite > Get User Email Detail By Role Invite Token"
)
def role_invite_get_email(transaction):
    """
    POST /role_invites/user
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        role_invite = RoleInviteFactory()
        db.session.add(role_invite)
        db.session.commit()


@hooks.before("Role Invites > Accept Role Invite > Accept Role Invite using Token")
def accept_role_invite_token(transaction):
    """
    POST /role_invites/accept-invite
    """
    transaction['skip'] = True


@hooks.before("Role Invites > Role Invite Details > Delete Role Invite")
def role_invite_delete(transaction):
    """
    DELETE /role-invites/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        role_invite = RoleInviteFactory()
        db.session.add(role_invite)
        db.session.commit()


# ------------------------- Users Events Roles -------------------------
@hooks.before(
    "Users Events Roles > Users Events Roles Collection List > List All Users Events Roles"
)
def users_events_roles_list(transaction):
    """
    GET /events/1/users-events-roles
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        users_events_roles = UsersEventsRolesFactory()
        db.session.add(users_events_roles)
        db.session.commit()


@hooks.before(
    "Users Events Roles > Users Events Roles Details > Users Events Roles Details"
)
def users_events_roles_get_detail(transaction):
    """
    GET /users-events-roles/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        users_events_roles = UsersEventsRolesFactory()
        db.session.add(users_events_roles)
        db.session.commit()


@hooks.before(
    "Users Events Roles > Users Events Roles Details > Update Users Events Roles"
)
def users_events_roles_patch(transaction):
    """
    PATCH /users-events-roles/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        users_events_roles = UsersEventsRolesSubFactory()
        db.session.add(users_events_roles)
        db.session.commit()


@hooks.before(
    "Users Events Roles > Users Events Roles Details > Delete Users Events Roles"
)
def users_events_roles_delete(transaction):
    """
    DELETE /users-events-roles/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        users_events_roles = UsersEventsRolesFactory()
        db.session.add(users_events_roles)
        db.session.commit()


# ------------------------- Upload -------------------------
@hooks.before("Upload > Image Upload > Upload an Image in temporary location")
def image_upload_post(transaction):
    """

    :param transaction:
    :return:
    """


@hooks.before("Upload > File Upload > Upload a File")
def file_upload_post(transaction):
    """

    :param transaction:
    :return:
    """
    transaction['skip'] = True


# ------------------------- Event Locations -------------------------
@hooks.before("Event Locations > Event Locations Collection > List All Event Locations")
def event_location_get_list(transaction):
    """
    GET /events-location
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_location = EventLocationFactory()
        db.session.add(event_location)
        db.session.commit()


# ------------------------- Event Types -------------------------
@hooks.before("Event Types > Event Types Collection > List All Event Types")
def event_type_get_list(transaction):
    """
    GET /events-types
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_type = EventTypeFactory()
        db.session.add(event_type)
        db.session.commit()


@hooks.before("Event Types > Event Types Collection > Create Event Type")
def event_type_post(transaction):
    """
    POST /events-types
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_type = EventTypeFactory()
        db.session.add(event_type)
        db.session.commit()


@hooks.before("Event Types > Event Type Details > Event Type Details")
def event_type_get_detail(transaction):
    """
    GET /event-types/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_type = EventTypeFactory()
        db.session.add(event_type)
        db.session.commit()


@hooks.before("Event Types > Event Type Details > Update Event Type")
def event_type_patch(transaction):
    """
    PATCH /event-types/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_type = EventTypeFactory()
        db.session.add(event_type)
        db.session.commit()


@hooks.before("Event Types > Event Type Details > Delete Event Type")
def event_type_delete(transaction):
    """
    DELETE /event-types/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_type = EventTypeFactory()
        db.session.add(event_type)
        db.session.commit()


@hooks.before("Event Types > Event Type of an Event > Event Type Details of an Event")
def event_event_type_get_detail(transaction):
    """
    GET /event/1/event-type
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_type = EventTypeFactory()
        db.session.add(event_type)

        event = EventFactoryBasic(event_type_id=1)
        db.session.add(event)
        db.session.commit()


# ------------------------- Event Topics -------------------------
@hooks.before("Event Topics > Event Topics Collection > List All Event Topics")
def event_topic_get_list(transaction):
    """
    GET /event-topics
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_topic = EventTopicFactory()
        db.session.add(event_topic)
        db.session.commit()


@hooks.before("Event Topics > Event Topics Collection > Create Event Topic")
def event_topic_post(transaction):
    """
    POST /event-topics
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_topic = EventTopicFactory()
        db.session.add(event_topic)
        db.session.commit()


@hooks.before("Event Topics > Event Topic Details > Event Topic Details")
def event_topic_get_detail(transaction):
    """
    GET /event-topics/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_topic = EventTopicFactory()
        db.session.add(event_topic)
        db.session.commit()


@hooks.before("Event Topics > Event Topic Details > Update Event Topic")
def event_topic_patch(transaction):
    """
    PATCH /event-topics/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_topic = EventTopicFactory()
        db.session.add(event_topic)
        db.session.commit()


@hooks.before("Event Topics > Event Topic Details > Delete Event Topic")
def event_topic_delete(transaction):
    """
    DELETE /event-topics/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_topic = EventTopicFactory()
        db.session.add(event_topic)
        db.session.commit()


@hooks.before("Event Topics > Event Topic of an Event > Event Topic Details of an Event")
def event_event_topic_get_detail(transaction):
    """
    GET /events/1/event-topic
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_topic = EventTopicFactory()
        db.session.add(event_topic)

        event = EventFactoryBasic(event_topic_id=1)
        db.session.add(event)
        db.session.commit()


@hooks.before(
    "Event Topics > Event Topic of a Sub Topic > Event Topic Details of a Sub Topic"
)
def sub_topic_event_topic_get_detail(transaction):
    """
    GET /sub-topics/1/event-topic
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_sub_topic = EventSubTopicFactory()
        db.session.add(event_sub_topic)
        db.session.commit()


# ------------------------- Event Sub Topics -------------------------
@hooks.before(
    "Event Sub Topics > Event Sub Topics Collection Get > List All Event Sub Topics"
)
def event_sub_topic_get_list(transaction):
    """
    GET /event-topics/1/event-sub-topics
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_sub_topic = EventSubTopicFactory()
        db.session.add(event_sub_topic)
        db.session.commit()


@hooks.before(
    "Event Sub Topics > Event Sub Topics Collection Post > Create Event Sub Topic"
)
def event_sub_topic_post(transaction):
    """
    POST /event-sub-topics
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_sub_topic = EventSubTopicFactory()
        db.session.add(event_sub_topic)
        db.session.commit()


@hooks.before("Event Sub Topics > Event Sub Topic Details > Event Sub Topic Details")
def event_sub_topic_get_detail(transaction):
    """
    GET /event-sub-topics/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_sub_topic = EventSubTopicFactory()
        db.session.add(event_sub_topic)
        db.session.commit()


@hooks.before("Event Sub Topics > Event Sub Topic Details > Update Event Sub Topic")
def event_sub_topic_patch(transaction):
    """
    PATCH /event-sub-topics/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_sub_topic = EventSubTopicFactory()
        db.session.add(event_sub_topic)
        db.session.commit()


@hooks.before("Event Sub Topics > Event Sub Topic Details > Delete Event Sub Topic")
def event_sub_topic_delete(transaction):
    """
    DELETE /event-sub-topics/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_sub_topic = EventSubTopicFactory()
        db.session.add(event_sub_topic)
        db.session.commit()


@hooks.before(
    "Event Sub Topics > Event Sub Topic of an Event > Event Sub Topic Details of an Event"
)
def event_event_sub_topic_get_detail(transaction):
    """
    GET /events/1/event-sub-topic
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_sub_topic = EventSubTopicFactory()
        db.session.add(event_sub_topic)

        event = EventFactoryBasic(event_sub_topic_id=1)
        db.session.add(event)
        db.session.commit()


@hooks.before(
    "Event Sub Topics > Event Sub Topic of Custom Placeholder > Event Sub Topic Details of Custom Placeholder"
)
def custom_placeholder_sub_topic_get_detail(transaction):
    """
    GET /custom-placeholders/1/event-sub-topic
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_sub_topic = EventSubTopicFactory()
        db.session.add(event_sub_topic)

        custom_placeholder = CustomPlaceholderFactory(event_sub_topic_id=1)
        db.session.add(custom_placeholder)
        db.session.commit()


# ------------------------- Custom Placeholders -------------------------
@hooks.before(
    "Custom Placeholders > Custom Placeholders Collection > List All Event Custom Placeholders"
)
def custom_placeholder_get_list(transaction):
    """
    GET /custom-placeholders
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        custom_placeholder = CustomPlaceholderFactory()
        db.session.add(custom_placeholder)
        db.session.commit()


@hooks.before(
    "Custom Placeholders > Custom Placeholders Collection > Create Custom Placeholder"
)
def custom_placeholder_post(transaction):
    """
    POST /custom-placeholders
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        custom_placeholder = CustomPlaceholderFactory()
        db.session.add(custom_placeholder)
        db.session.commit()


@hooks.before(
    "Custom Placeholders > Custom Placeholder Details > Custom Placeholder Details"
)
def custom_placeholder_get_detail(transaction):
    """
    GET /custom-placeholders/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        custom_placeholder = CustomPlaceholderFactory()
        db.session.add(custom_placeholder)
        db.session.commit()


@hooks.before(
    "Custom Placeholders > Custom Placeholder Details > Update Custom Placeholder"
)
def custom_placeholder_patch(transaction):
    """
    PATCH /custom-placeholders/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        custom_placeholder = CustomPlaceholderFactory()
        db.session.add(custom_placeholder)
        db.session.commit()


@hooks.before(
    "Custom Placeholders > Custom Placeholder Details > Delete Custom Placeholder"
)
def custom_placeholder_delete(transaction):
    """
    DELETE /custom-placeholders/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        custom_placeholder = CustomPlaceholderFactory()
        db.session.add(custom_placeholder)
        db.session.commit()


@hooks.before(
    "Custom Placeholders > Custom Placeholder Details of Event Sub-topic >"
    " Custom Placeholder Details of Event Sub-topic"
)
def event_sub_topic_custom_placeholder_get_detail(transaction):
    """
    GET /event-sub-topics/1/custom-placeholder
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_sub_topic = EventSubTopicFactory()
        db.session.add(event_sub_topic)

        custom_placeholder = CustomPlaceholderFactory(event_sub_topic_id=1)
        db.session.add(custom_placeholder)
        db.session.commit()


# ------------------------- User Permissions -------------------------
@hooks.before("User Permissions > User Permission Collection > List all user permissions")
def user_permission_get_list(transaction):
    """
    GET /user-permissions
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        user_permission = UserPermissionFactory()
        db.session.add(user_permission)
        db.session.commit()


@hooks.before("User Permissions > User Permission Details > Get User Permission Details")
def user_permission_get_detail(transaction):
    """
    GET /user-permissions/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        user_permission = UserPermissionFactory()
        db.session.add(user_permission)
        db.session.commit()


@hooks.before("User Permissions > User Permission Details > Update User Permission")
def user_permission_patch(transaction):
    """
    PATCH /user-permissions/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        user_permission = UserPermissionFactory()
        db.session.add(user_permission)
        db.session.commit()


@hooks.before("User Permissions > User Permission Details > Delete User Permission")
def user_permission_delete(transaction):
    """
    DELETE /user-permissions/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        user_permission = UserPermissionFactory()
        db.session.add(user_permission)
        db.session.commit()


# ------------------------- Stripe Authorizations -------------------------
@hooks.before(
    "Stripe Authorization > Stripe Authorization Collection > Create Stripe Authorization"
)
def stripe_authorization_post(transaction):
    """
    POST /stripe-authorization
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before(
    "Stripe Authorization > Stripe Authorization Details > Get Stripe Authorization"
)
def stripe_authorization_get_detail(transaction):
    """
    GET /stripe-authorization/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        stripe = StripeAuthorizationFactory()
        db.session.add(stripe)
        db.session.commit()


@hooks.before(
    "Stripe Authorization > Stripe Authorization Details > Update Stripe Authorization"
)
def stripe_authorization_patch(transaction):
    """
    PATCH /stripe-authorization/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        stripe = StripeAuthorizationFactory()
        db.session.add(stripe)
        db.session.commit()


@hooks.before(
    "Stripe Authorization > Stripe Authorization Details > Delete Stripe Authorization"
)
def stripe_authorization_delete(transaction):
    """
    DELETE /stripe-authorization/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        stripe = StripeAuthorizationFactory()
        db.session.add(stripe)
        db.session.commit()


@hooks.before(
    "Stripe Authorization > Stripe Authorization for an Event > Get Stripe Authorization Details of an Event"
)
def event_stripe_authorization_get_detail(transaction):
    """
    GET /events/1/stripe-authorization
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        stripe = StripeAuthorizationFactory()
        db.session.add(stripe)
        db.session.commit()


# ------------------------- Export -------------------------
@hooks.before(
    "Event Export > Start Event Export as Zip > Start a Task to Export an Event as Zip"
)
def event_export_post(transaction):
    """
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before(
    "Event Export > Start Event Export as iCal file > Start a Task to Export an Event as iCal event"
)
def event_export_ical_get(transaction):
    """
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before(
    "Event Export > Start Event Export as xCalendar > Start a Task to Export an Event as xCalendar"
)
def event_export_xcal_get(transaction):
    """
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before(
    "Event Export > Start Event Export as Pentabarf XML > Start a Task to Export an Event as Pentabarf XML"
)
def event_export_pentabarf_get(transaction):
    """
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before(
    "Event Export > Start Orders Export as CSV > Start a Task to Export Orders of an Event as CSV"
)
def event_orders_export_csv_get(transaction):
    """
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before(
    "Event Export > Start Orders Export as PDF > Start a Task to Export Orders of an Event as PDF"
)
def event_orders_export_pdf_get(transaction):
    """
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before(
    "Event Export > Start Attendees Export as CSV > Start a Task to Export Attendees of an Event as CSV"
)
def event_attendees_export_csv_get(transaction):
    """
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before(
    "Event Export > Start Attendees Export as PDF > Start a Task to Export Attendees of an Event as PDF"
)
def event_attendees_export_pdf_get(transaction):
    """
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before(
    "Event Export > Start Sessions Export as CSV > Start a Task to Export Sessions of an Event as CSV"
)
def event_sessions_export_csv_get(transaction):
    """
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before(
    "Event Export > Start Speakers Export as CSV > Start a Task to Export Speakers of an Event as CSV"
)
def event_speakers_export_csv_get(transaction):
    """
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before(
    "Event Export > Start Sessions Export as PDF > Start a Task to Export Sessions of an Event as PDF"
)
def event_sessions_export_pdf_get(transaction):
    """
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before(
    "Event Export > Start Speakers Export as PDF > Start a Task to Export Speakers of an Event as PDF"
)
def event_speakers_export_pdf_get(transaction):
    """
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


# ------------------------- Import -------------------------
@hooks.before("Event Import > Start Event Import > Start a Task to Import an Event")
def event_import_post(transaction):
    """
    :param transaction:
    :return:
    """
    transaction['skip'] = True


# ------------------------- Celery Task -------------------------
@hooks.before("Celery Tasks > Task Details > Get Task Result")
def celery_task_get(transaction):
    """

    :param transaction:
    :return:
    """
    transaction['skip'] = True


# ------------------------- Event Statistics -------------------------


@hooks.before(
    "Event Statistics > Event Statistics Details > Show Event Statistics General"
)
def event_statistics_general_get(transaction):
    """
    GET /events/1/general-statistics
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


# ------------------------- Order Statistics -------------------------


@hooks.before(
    "Order Statistics > Order Statistics Details By Event > Show Order Statistics By Event"
)
def order_statistics_event_get(transaction):
    """
    GET /events/1/order-statistics
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        ticket = TicketFactory()
        db.session.add(ticket)
        db.session.commit()


@hooks.before(
    "Order Statistics > Order Statistics Details By Ticket > Show Order Statistics By Ticket"
)
def order_statistics_ticket_get(transaction):
    """
    GET /tickets/1/order-statistics
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        ticket = TicketFactory()
        db.session.add(ticket)
        db.session.commit()


# ------------------------- Orders -------------------------


@hooks.before("Orders > Orders Collection > List All Orders")
def orders_get_collection(transaction):
    """
    GET /orders
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        order = OrderFactory()
        db.session.add(order)
        db.session.commit()


@hooks.before("Orders > Create Order > Create Order")
def create_order(transaction):
    """
    POST /orders/create-order
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        discount_code = DiscountCodeTicketSubFactory(
            type='percent', value=10.0, tickets=[]
        )
        _create_taxed_tickets(db, tax_included=False, discount_code=discount_code)
        db.session.commit()


@hooks.before("Orders > Calculate Order Amount > Calculate Order Amount")
def calculate_amount(transaction):
    """
    POST /orders/calculate-amount
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        discount_code = DiscountCodeTicketSubFactory(
            type='percent', value=10.0, tickets=[]
        )
        _create_taxed_tickets(db, tax_included=False, discount_code=discount_code)
        db.session.commit()


@hooks.before(
    "Orders > Create Order with on site Attendees > Create Order with on site Attendees"
)
def create_order_with_on_site_attendee(transaction):
    """
    POST /orders?onsite=true
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Orders > Order Detail > Get Order Detail")
def order_detail(transaction):
    """
    GET /orders
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        order = OrderFactory()
        db.session.add(order)
        db.session.commit()


@hooks.before("Orders > Order Detail > Update Order")
def update_order(transaction):
    """
    GET /orders
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        order = OrderFactory()
        db.session.add(order)
        db.session.commit()


@hooks.before("Orders > Order Detail > Delete Order")
def delete_order(transaction):
    """
    GET /orders
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        order = OrderFactory()
        db.session.add(order)
        db.session.commit()


@hooks.before("Orders > Orders under an Event > List all Orders under an Event")
def event_order_get_list(transaction):
    """
    GET /events/1/orders
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        order = OrderFactory(event_id=event.id)
        db.session.add(event)
        db.session.add(order)
        db.session.commit()


@hooks.before("Orders > Charge > Charge for an Order")
def orders_charge(transaction):
    """
    GET /orders/1/charge
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Orders > Orders under a User > List all Orders under a User")
def orders_get_collection_under_user(transaction):
    """
    GET /users/1/orders
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Orders > Create Paypal payment > Create Paypal payment for an Order")
def create_paypal_payment(transaction):
    """
    POST /v1/orders/{identifier}/create-paypal-payment
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Event Copy > Create Event Copy > Create Copy")
def create_event_copy(transaction):
    """
    GET /v1/events/{identifier}/copy
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before("Events > Get Event for a Order > Event Details for a Order")
def get_event_from_order(transaction):
    """
    GET /v1/orders/{identifier}/event
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        order = OrderFactory()
        order.identifier = "7201904e"
        db.session.add(order)
        db.session.commit()


@hooks.before("Change Password > Reset Forgotten Password > Reset Password from Token")
def reset_password_patch(transaction):
    """
    PATCH /v1/auth/reset-password
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        user = UserFactory(is_verified=True)
        user.reset_password = 'token'
        db.session.add(user)
        db.session.commit()


@hooks.before("Email Verification > Verify Email > Verify the email via auth token")
def verify_email_from_token(transaction):
    """
    POST /v1/auth/verify-email
    :param transaction:
    :return:
    """
    transaction['skip'] = True


# ------------------------- Custom System Role -------------------------


@hooks.before(
    "Custom System Roles > Custom System Roles Collections > List All Custom System Roles"
)
def custom_system_roles_get_list(transaction):
    """
    GET /custom-system-roles
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        custom_system_role = CustomSysRoleFactory()
        db.session.add(custom_system_role)
        db.session.commit()


@hooks.before("Custom System Roles > Custom System Roles Details > Get Details")
def custom_system_role_get_detail(transaction):
    """
    GET /custom-system-roles/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        custom_system_role = CustomSysRoleFactory()
        db.session.add(custom_system_role)
        db.session.commit()


@hooks.before(
    "Custom System Roles > Custom System Roles Details > Update Custom System Role"
)
def custom_system_role_patch(transaction):
    """
    PATCH /custom-system-roles/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        custom_system_role = CustomSysRoleFactory()
        db.session.add(custom_system_role)
        db.session.commit()


@hooks.before(
    "Custom System Roles > Custom System Roles Details > Delete Custom Systen Role"
)
def custom_system_role_delete(transaction):
    """
    DELETE /custom-system-roles/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        custom_system_role = CustomSysRoleFactory()
        db.session.add(custom_system_role)
        db.session.commit()


@hooks.before(
    "Custom System Roles > Get Custom System Role Details for a Panel Permission > "
    "Get Custom System Role Details for a Panel Permission"
)
def custom_system_roles_panel_permission(transaction):
    """
    GET /panel-permissions/1/custom-system-roles
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        panel_permission = PanelPermissionFactory()
        db.session.add(panel_permission)
        db.session.commit()


# ------------------------- Panel Permission -------------------------


@hooks.before(
    "Panel Permissions > Panel Permissions Collections > List All Panel Permissions"
)
def panel_permission_get_list(transaction):
    """
    GET /panel-permissions
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        panel_permission = PanelPermissionFactory()
        db.session.add(panel_permission)
        db.session.commit()


@hooks.before("Panel Permissions > Panel Permission Details > Get Details")
def panel_permission_get_detail(transaction):
    """
    GET /panel-permissions/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        panel_permission = PanelPermissionFactory()
        db.session.add(panel_permission)
        db.session.commit()


@hooks.before("Panel Permissions > Panel Permission Details > Update Panel Permission")
def panel_permission_patch(transaction):
    """
    PATCH /panel-permissions/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        panel_permission = PanelPermissionFactory()
        db.session.add(panel_permission)
        db.session.commit()


@hooks.before("Panel Permissions > Panel Permission Details > Delete Panel Permission")
def panel_permission_delete(transaction):
    """
    DELETE /panel-permissions/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        panel_permission = PanelPermissionFactory()
        db.session.add(panel_permission)
        db.session.commit()


@hooks.before(
    "Panel Permissions > Get Panel Permission Details for a Custom System Role > "
    "Get Panel Permission Details for a Custom System Role"
)
def panel_permissions_custom_system_role(transaction):
    """
    GET /custom-system-roles/1/panel-permissions
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        CustomSysRoleFactory()
        PanelPermissionFactory()
        db.session.commit()


# ------------------------- User Favourite Events -------------------------


@hooks.before(
    "Favourite Events > Favourite Events Collection > List All Favourite Events"
)
def favourite_events_list_get(transaction):
    """
    GET /user-favourite-events
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        user_fav_event = UserFavouriteEventFactory()
        db.session.add(user_fav_event)
        db.session.commit()


@hooks.before("Favourite Events > Favourite Events Collection > Create a Favourite Event")
def favourite_events_list_post(transaction):
    """
    POST /user-favourite-events
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before("Favourite Events > Favourite Events Detail > Get Details")
def favourite_event_details_get(transaction):
    """
    GET /user-favourite-events/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        user_fav_event = UserFavouriteEventFactory()
        db.session.add(user_fav_event)
        db.session.commit()


@hooks.before("Favourite Events > Favourite Events Detail > Delete Favourite Event")
def favourite_event_delete(transaction):
    """
    DELETE /user-favourite-events/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        user_fav_event = UserFavouriteEventFactory()
        db.session.add(user_fav_event)
        db.session.commit()


# ------------------------- User Favourite Sessions -------------------------


@hooks.before(
    "Favourite Sessions > Favourite Sessions Collection List > List All Favourite Sessions"
)
def favourite_sessions_list_get(transaction):
    """
    GET /user-favourite-sessions
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        user_fav_session = UserFavouriteSessionFactory()
        db.session.add(user_fav_session)
        db.session.commit()


@hooks.before(
    "Favourite Sessions > Favourite Sessions Collection > Create a Favourite Session"
)
def favourite_sessions_list_post(transaction):
    """
    POST /user-favourite-sessions
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        track = TrackFactoryBase()
        session = SessionSubFactory(event=event, track=track)
        db.session.add(session)
        db.session.commit()


@hooks.before("Favourite Sessions > Favourite Sessions Detail > Get Details")
def favourite_session_details_get(transaction):
    """
    GET /user-favourite-sessions/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        user_fav_session = UserFavouriteSessionFactory()
        db.session.add(user_fav_session)
        db.session.commit()


@hooks.before("Favourite Sessions > Favourite Sessions Detail > Delete Favourite Session")
def favourite_session_delete(transaction):
    """
    DELETE /user-favourite-sessions/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        user_fav_session = UserFavouriteSessionFactory()
        db.session.add(user_fav_session)
        db.session.commit()


@hooks.before(
    "Favourite Sessions > Favourite Sessions Collection List > List All Favourite Sessions of a Session"
)
def favourite_sessions_list_get_under_session(transaction):
    """
    GET /v1/sessions/1/user-favourite-sessions
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        user_fav_session = UserFavouriteSessionFactory()
        db.session.add(user_fav_session)
        db.session.commit()


@hooks.before(
    "Favourite Sessions > Favourite Sessions Collection List > List All Favourite Sessions of an Event"
)
def favourite_sessions_list_get_under_event(transaction):
    """
    GET /v1/sessions/1/user-favourite-sessions
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        user_fav_session = UserFavouriteSessionFactory()
        db.session.add(user_fav_session)
        db.session.commit()


# ------------------------- Admin Statistics -------------------------


@hooks.before("Admin Statistics > Event Statistics Details > Show Event Statistics")
def event_statistics_get(transaction):
    """
    GET /admin/statistics/events
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before(
    "Admin Statistics > Event Types Statistics Details > Show Event Types Statistics"
)
def event_type_statistics_get(transaction):
    """
    GET /admin/statistics/event-types
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_type = EventTypeFactory()
        db.session.add(event_type)
        db.session.commit()


@hooks.before(
    "Admin Statistics > Event Topics Statistics Details > Show Event Topics Statistics"
)
def event_topic_statistics_get(transaction):
    """
    GET /admin/statistics/event-topics
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_topic = EventTopicFactory()
        db.session.add(event_topic)
        db.session.commit()


@hooks.before("Admin Statistics > User Statistics Details > Show User Statistics")
def user_statistics_get(transaction):
    """
    GET /admin/statistics/users
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        user = UserFactory()
        db.session.add(user)
        db.session.commit()


@hooks.before("Admin Statistics > Session Statistics Details > Show Session Statistics")
def session_statistics_get(transaction):
    """
    GET /admin/statistics/sessions
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        session = SessionFactory()
        db.session.add(session)
        db.session.commit()


@hooks.before("Admin Statistics > Mail Statistics Details > Show Mail Statistics")
def mail_statistics_get(transaction):
    """
    GET /admin/statistics/mails
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        mail = MailFactory()
        db.session.add(mail)
        db.session.commit()


# ------------------------- Exhibitors -------------------------
@hooks.before("Exhibitors > Exhibitors Get Collection > List All Exhibitors")
def exhibitor_get_list(transaction):
    """
    GET /events/1/exhibitors
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        ExhibitorFactory()
        db.session.commit()


@hooks.before("Exhibitors > Exhibitors Post Collection > Create Exhibitor")
def exhibitor_post(transaction):
    """
    POST /exhibitors
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        EventFactoryBasic()
        db.session.commit()


@hooks.before("Exhibitors > Exhibitor Details > Exhibitor Details")
def exhibitor_get_detail(transaction):
    """
    GET /exhibitors/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        ExhibitorFactory()
        db.session.commit()


@hooks.before("Exhibitors > Exhibitor Details > Update Exhibitor")
def exhibitor_patch(transaction):
    """
    PATCH /exhibitors/1
    :param transaction:
    :return:
    """

    with stash['app'].app_context():
        ExhibitorFactory()
        db.session.commit()


@hooks.before("Exhibitors > Exhibitor Details > Delete Exhibitor")
def exhibitor_delete(transaction):
    """
    DELETE /exhibitors/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        ExhibitorFactory()
        db.session.commit()


@hooks.before(
    "Attendees > Search Attendees under an event > Search All Attendees under an event"
)
def search_attendees_from_event(transaction):
    """
    GET /v1/events/{event_id}/attendees/search
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before("Badge Forms > Get Badge Form By Ticket > Get Badge Form By Ticket")
def get_badge_form_by_ticket(transaction):
    """
    GET /v1/ticket/{ticket_id}/badge-forms
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        ticket = TicketFactory(
            event=event,
            badge_id='example',
        )
        badge_form = BadgeFormFactory(
            event=event,
            badge_id=ticket.badge_id,
        )
        BadgeFieldFormFactory(
            badge_form=badge_form,
            badge_id=ticket.badge_id,
        )
        db.session.commit()


@hooks.before(
    "Station Store Paxs > Create Station Store Paxs > Create Station Store Paxs"
)
def create_station_store_pax(transaction):
    """
    POST /v1/station-store-paxs
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        microlocation = MicrolocationSubFactory(
            event=event,
        )
        StationFactory(
            event=event, microlocation=microlocation, station_type='registration'
        )
        SessionSubFactory(
            event=event,
            microlocation=microlocation,
        )
        db.session.commit()


@hooks.before(
    "Station Store Paxs > Get Station Store Paxs By Station and Session > Get Station Store Paxs By Station and Session"
)
def get_station_store_pax_by_station_session(transaction):
    """
    GET /v1/stations/{station_id}/sessions/{session_id}/station-store-paxs
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        microlocation = MicrolocationSubFactory(
            event=event,
        )
        station = StationFactory(
            event=event, microlocation=microlocation, station_type='registration'
        )
        session = SessionSubFactory(
            event=event,
            microlocation=microlocation,
        )
        StationStorePaxFactory(
            current_pax=10,
            station=station,
            session=session,
        )
        db.session.commit()


@hooks.before("Stations > Create Station > Create Station")
def create_station(transaction):
    """
    POST /v1/station
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        MicrolocationSubFactory(
            event=event,
        )
        db.session.commit()


@hooks.before("Stations > Get Station > Get Station")
def get_station(transaction):
    """
    GET /v1/stations/{station_id}
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        microlocation = MicrolocationSubFactory(
            event=event,
        )
        StationFactory(
            event=event,
            microlocation=microlocation,
        )
        db.session.commit()


@hooks.before("Stations > Get Stations by Event > Get Stations by Event")
def get_stations_by_event(transaction):
    """
    GET /v1/events/{event_id}/stations
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        microlocation = MicrolocationSubFactory(
            event=event,
        )
        StationFactory(
            event=event,
            microlocation=microlocation,
        )
        db.session.commit()


@hooks.before("Users Check In > Create User Check In > Create User Check In")
def create_user_check_in(transaction):
    """
    POST /v1/user-check-in
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        microlocation = MicrolocationSubFactory(
            event=event,
        )
        ticket = TicketFactory(
            event=event,
        )
        StationSubFactory(
            event=event, microlocation=microlocation, station_type='registration'
        )
        SessionSubFactory(
            event=event,
            microlocation=microlocation,
        )
        AttendeeSubFactory(
            event=event,
            ticket=ticket,
        )
        db.session.commit()


@hooks.before(
    "Event Export > Start Badge Export as PDF > Start a Task to Export Badge of an Event as PDF"
)
def badge_export_pdf_get(transaction):
    """
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        ticket = TicketFactory(
            event=event,
            badge_id='example',
        )
        badge_form = BadgeFormFactory(
            event=event,
            badge_id=ticket.badge_id,
        )
        BadgeFieldFormFactory(
            badge_form=badge_form,
            badge_id=ticket.badge_id,
        )
        AttendeeFactory(ticket_id=1)
        db.session.commit()


@hooks.before(
    "Translation Channels > Translation Channels > List all Translation Channels"
)
def list_all_translation(transaction):
    """
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        video_stream = VideoStreamFactoryBase()
        TranslationChannelFactory(video_stream=video_stream)
        db.session.commit()


@hooks.before(
    "Translation Channels > Translation Channels > List all Translation Channels Of Video Stream"
)
def list_all_translation_of_video_stream(transaction):
    """
    :param transaction: transaction
    :return:
    """
    with stash['app'].app_context():
        video_stream = VideoStreamFactoryBase()
        TranslationChannelFactory(video_stream=video_stream)
        db.session.commit()
