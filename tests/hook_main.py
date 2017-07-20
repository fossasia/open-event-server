import sys
import os.path as path
import dredd_hooks as hooks
import requests

# DO NOT REMOVE THIS. This adds the project root for successful imports. Imports from the project directory should be
# placed only below this
sys.path.insert(1, path.abspath(path.join(__file__, "../..")))

from flask_migrate import Migrate, stamp
from flask import Flask
from app.models import db
from populate_db import populate_without_print

# imports from factories
from app.factories.user import UserFactory
from app.factories.notification import NotificationFactory
from app.factories.event import EventFactoryBasic
from app.factories.social_link import SocialLinkFactory
from app.factories.microlocation import MicrolocationFactory
from app.factories.image_size import ImageSizeFactory
from app.factories.page import PageFactory
from app.factories.event_copyright import EventCopyrightFactory
from app.factories.setting import SettingFactory
from app.factories.event_type import EventTypeFactory
from app.factories.discount_code import DiscountCodeFactory
from app.factories.access_code import AccessCodeFactory
from app.factories.event_topic import EventTopicFactory
from app.factories.event_invoice import EventInvoiceFactory
from app.factories.event_sub_topic import EventSubTopicFactory
from app.factories.sponsor import SponsorFactory
from app.factories.speakers_call import SpeakersCallFactory
from app.factories.tax import TaxFactory
from app.factories.session import SessionFactory
from app.factories.speaker import SpeakerFactory
from app.factories.ticket import TicketFactory
from app.factories.attendee import AttendeeFactory
from app.factories.session_type import SessionTypeFactory
from app.factories.track import TrackFactory
from app.factories.ticket_tag import TicketTagFactory
from app.factories.role import RoleFactory
from app.factories.module import ModuleFactory
from app.factories.ticket_fee import TicketFeesFactory
from app.factories.role_invite import RoleInviteFactory
from app.factories.users_events_role import UsersEventsRoleFactory
from app.factories.custom_placeholder import CustomPlaceholderFactory
from app.factories.user_permission import UserPermissionFactory
from app.factories.email_notification import EmailNotificationFactory
from app.factories.activities import ActivityFactory

stash = {}
api_username = "open_event_test_user@fossasia.org"
api_password = "fossasia"
api_uri = "http://localhost:5000/auth/session"


def obtain_token():
    data = {
        "email": api_username,
        "password": api_password
    }
    url = api_uri
    response = requests.post(url, json=data)
    response.raise_for_status()
    parsed_body = response.json()
    token = parsed_body["access_token"]
    return token


def create_super_admin(email, password):
    user = UserFactory(email=email, password=password, is_super_admin=True,
                       is_admin=True, is_verified=True)
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
        db.create_all()
        stamp()
        create_super_admin(api_username, api_password)
        populate_without_print()

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
def skip_auth(transaction):
    """
    POST /auth/session
    :param transaction:
    :return:
    """
    transaction['request']['headers']['Authorization'] = ""
    with stash['app'].app_context():
        user = UserFactory(email="email@example.com", password="password", is_verified=True)
        db.session.add(user)
        db.session.commit()
        print('User Created')


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
    pass


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
    pass


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


# ------------------------- Copyright -------------------------
@hooks.before("Copyright > Event Copyright > Create Event Copyright")
def copyright_post(transaction):
    """
    POST /events/1/event-copyright
    :param transaction:
    :return:
    """
    # Skip until docs for direct endpoints added
    transaction['skip'] = True

    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before("Copyright > Event Copyright Details > Event Copyright Details")
def copyright_get_detail(transaction):
    """
    GET /event-copyright/1
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
    PATCH /event-copyright/1
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
    DELETE /event-copyright/1
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
    GET /events/1/event-invoices
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_invoice = EventInvoiceFactory()
        db.session.add(event_invoice)
        db.session.commit()


@hooks.before("Invoices > Event Invoices > Create Event Invoices")
def invoice_post(transaction):
    """
    POST /events/1/event-invoices
    :param transaction:
    :return:
    """
    # Skip until docs for direct endpoints added
    transaction['skip'] = True

    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
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


# ------------------------- Microlocation -------------------------
@hooks.before("Microlocations > Microlocation Collection > List All Microlocations")
def microlocation_get_list(transaction):
    """
    GET /events/1/microlocations
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        microlocation = MicrolocationFactory()
        db.session.add(microlocation)
        db.session.commit()


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


@hooks.before("Microlocations > Microlocation Details > Mictolocation Details")
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


# ------------------------- Sessions -------------------------
@hooks.before("Sessions > Sessions Collection > List All Sessions")
def session_get_list(transaction):
    """
    GET /events/1/sessions
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        session = SessionFactory()
        db.session.add(session)
        db.session.commit()


@hooks.before("Sessions > Sessions Collection > Create Sessions")
def session_post(transaction):
    """
    POST /events/1/sessions
    :param transaction:
    :return:
    """
    # Skip until docs for direct endpoints added
    transaction['skip'] = True

    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
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
        db.session.add(session)
        db.session.commit()


# ------------------------- Session Type -------------------------
@hooks.before("Session Type > Session Type Collection > List All Session Types")
def session_type_get_list(transaction):
    """
    GET /events/1/session-types
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        session_type = SessionTypeFactory()
        db.session.add(session_type)
        db.session.commit()


@hooks.before("Session Type > Session Type Collection > Create Session Type")
def session_type_post(transaction):
    """
    POST /events/1/session-types
    :param transaction:
    :return:
    """
    # Skip until docs for direct endpoints added
    transaction['skip'] = True

    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
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


# ------------------------- Speaker -------------------------
@hooks.before("Speakers > Speakers Collection > List All Speakers")
def speaker_get_list(transaction):
    """
    GET /events/1/speakers
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        speaker = SpeakerFactory()
        db.session.add(speaker)
        db.session.commit()


@hooks.before("Speakers > Speakers Collection > Create Speaker")
def speaker_post(transaction):
    """
    POST /events/1/speakers
    :param transaction:
    :return:
    """
    # Skip until docs for direct endpoints added
    transaction['skip'] = True

    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before("Speakers > Speaker > Speaker Details")
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


@hooks.before("Speakers > Speaker > Update Speaker")
def speaker_patch(transaction):
    """
    PATCH /speakers/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        speaker = SpeakerFactory()
        db.session.add(speaker)
        db.session.commit()


@hooks.before("Speakers > Speaker > Delete Speaker")
def speaker_delete(transaction):
    """
    DELETE /speakers/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        speaker = SpeakerFactory()
        db.session.add(speaker)
        db.session.commit()


# ------------------------- Social Links -------------------------
@hooks.before("Social Links > Social Links Collection > List All Social Links")
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


@hooks.before("Social Links > Social Links Collection > Create Social Link")
def social_link_post(transaction):
    """
    POST /events/1/social-links
    :param transaction:
    :return:
    """
    # Skip until docs for direct endpoints added
    transaction['skip'] = True

    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
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
@hooks.before("Speakers Calls > Speakers Call Collection > Get Speakers Call")
def speakers_call_get(transaction):
    """
    GET /events/1/speakers-call
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        speakers_call = SpeakersCallFactory()
        db.session.add(speakers_call)
        db.session.commit()


@hooks.before("Speakers Calls > Speakers Call Collection > Create Speakers Call")
def speakers_call_post(transaction):
    """
    POST /events/1/speakers-call
    :param transaction:
    :return:
    """
    # Skip until docs for direct endpoints added
    transaction['skip'] = True

    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


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


# ------------------------- Sponsors -------------------------
@hooks.before("Sponsors > Sponsors Collection > List All Sponsors")
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


@hooks.before("Sponsors > Sponsors Collection > Create Sponsor")
def sponsor_post(transaction):
    """
    POST /events/1/sponsors
    :param transaction:
    :return:
    """
    # Skip until docs for direct endpoints added
    transaction['skip'] = True

    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
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
    # Skip until docs for direct endpoints added
    transaction['skip'] = True

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
    GET /tax/1
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
    PATCH /tax/1
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
    PATCH /tax/1
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
    DELETE /tax/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        tax = TaxFactory()
        db.session.add(tax)
        db.session.commit()


# ------------------------- Tickets -------------------------
@hooks.before("Tickets > Tickets Collection > List All Tickets")
def ticket_get_list(transaction):
    """
    GET /events/1/tickets
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        ticket = TicketFactory()
        db.session.add(ticket)
        db.session.commit()


@hooks.before("Tickets > Tickets Collection > Create Ticket")
def ticket_post(transaction):
    """
    POST /events/1/tickets
    :param transaction:
    :return:
    """
    # Skip until docs for direct endpoints added
    transaction['skip'] = True

    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
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
    pass


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
@hooks.before("Ticket Tags > Ticket Tags Collection > List All Ticket Tags")
def ticket_tag_get_list(transaction):
    """
    GET /tickets/1/ticket-tags
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        ticket_tag = TicketTagFactory()
        db.session.add(ticket_tag)
        db.session.commit()


@hooks.before("Ticket Tags > Ticket Tags Collection > Create Ticket Tag")
def ticket_tag_post(transaction):
    """
    POST /tickets/1/ticket-tags
    :param transaction:
    :return:
    """
    # Skip until docs for direct endpoints added
    transaction['skip'] = True

    with stash['app'].app_context():
        tickets = TicketFactory()
        db.session.add(tickets)
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


# ---------------------- Attendees (Ticket Holder) ---------------------
@hooks.before("Attendees > Attendees Collection > List All Attendees")
def attendee_get_list(transaction):
    """
    GET /events/1/attendees
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        attendee = AttendeeFactory()
        db.session.add(attendee)
        db.session.commit()


@hooks.before("Attendees > Attendees Collection > Create Attendee")
def attendee_post(transaction):
    """
    POST /events/1/attendees
    :param transaction:
    :return:
    """
    # Skip until docs for direct endpoints added
    transaction['skip'] = True


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
        attendee = AttendeeFactory()
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
        attendee = AttendeeFactory()
        db.session.add(attendee)
        db.session.commit()


# ------------------------- Tracks -------------------------
@hooks.before("Tracks > Tracks Collection > List All Tracks")
def track_get_list(transaction):
    """
    GET /events/1/tracks
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        track = TrackFactory()
        db.session.add(track)
        db.session.commit()


@hooks.before("Tracks > Tracks Collection > Create Track")
def track_post(transaction):
    """
    POST /events/1/tracks
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
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


# ------------------------- Notifications -------------------------
@hooks.before("Notifications > Notifications Collection > List All Notifications")
def notification_get_list(transaction):
    """
    GET /users/2/notifications
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        notification = NotificationFactory()
        db.session.add(notification)
        db.session.commit()


@hooks.before("Notifications > Notifications Collection > Create Notificaiton")
def notification_post(transaction):
    """
    POST /users/2/notifications
    :param transaction:
    :return:
    """
    # Skip until docs for direct endpoints added
    transaction['skip'] = True

    with stash['app'].app_context():
        user = UserFactory()
        db.session.add(user)
        db.session.commit()


@hooks.before("Notifications > Notification Detail > Notification Detail")
def notification_get_detail(transaction):
    """
    GET /notifications/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        notification = NotificationFactory()
        db.session.add(notification)
        db.session.commit()


@hooks.before("Notifications > Notification Detail > Update Notification")
def notification_patch(transaction):
    """
    PATCH /notifications/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        notification = NotificationFactory()
        db.session.add(notification)
        db.session.commit()


@hooks.before("Notifications > Notification Detail > Delete Notification")
def notification_delete(transaction):
    """
    DELETE /notifications/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        notification = NotificationFactory()
        db.session.add(notification)
        db.session.commit()


# ------------------------- Email Notifications -------------------------
@hooks.before("Email Notifications > Email Notifications Collection > List All Email Notifications")
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


@hooks.before("Email Notifications > Email Notifications Collection > Create Email Notificaiton")
def email_notification_post(transaction):
    """
    POST /users/2/email-notifications
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        user = UserFactory()
        db.session.add(user)
        db.session.add(event)
        db.session.commit()


@hooks.before("Email Notifications > Email Notification Detail > Email Notification Detail")
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


@hooks.before("Email Notifications > Email Notification Detail > Update Email Notification")
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


@hooks.before("Email Notifications > Email Notification Detail > Delete Email Notification")
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


# ------------------------- Image Size -------------------------
@hooks.before("Image Size > Image Size Collection > List Image Sizes")
def image_size_get_list(transaction):
    """
    GET /image-sizes
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        image_size = ImageSizeFactory()
        db.session.add(image_size)
        db.session.commit()


@hooks.before("Image Size > Image Size Collection > Create Image Size")
def image_size_post(transaction):
    """
    POST /image-sizes
    :param transaction:
    :return:
    """
    pass


@hooks.before("Image Size > Image Size Details > Get Image Size Details")
def image_size_get_detail(transaction):
    """
    GET /image-sizes/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        image_size = ImageSizeFactory()
        db.session.add(image_size)
        db.session.commit()


@hooks.before("Image Size > Image Size Details > Update Image Size")
def image_size_patch(transaction):
    """
    PATCH /image-sizes/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        image_size = ImageSizeFactory()
        db.session.add(image_size)
        db.session.commit()


@hooks.before("Image Size > Image Size Details > Delete Image Size")
def image_size_delete(transaction):
    """
    DELETE /image-sizes/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        image_size = ImageSizeFactory()
        db.session.add(image_size)
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
    pass


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
        role = RoleFactory()
        db.session.add(role)
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
    pass


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


# ------------------------- Modules -------------------------
@hooks.before("Modules > Modules Details > Show Modules")
def modules_get_list(transaction):
    """
    GET /modules
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        module = ModuleFactory()
        db.session.add(module)
        db.session.commit()


@hooks.before("Modules > Modules Details > Update Modules")
def modules_patch(transaction):
    """
    PATCH /modules
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        module = ModuleFactory()
        db.session.add(module)
        db.session.commit()


# ------------------------- Discount Codes -------------------------
@hooks.before("Discount Codes > Event Discount Code Collection > List All Event Discount Codes")
def event_discount_code_get_list(transaction):
    """
    GET /discount-codes
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        discount_code = DiscountCodeFactory()
        db.session.add(discount_code)
        db.session.commit()


@hooks.before("Discount Codes > Event Discount Code Collection > Create Event Discount Code")
def event_discount_code_post(transaction):
    """
    POST /discount-codes
    :param transaction:
    :return:
    """
    pass


@hooks.before("Discount Codes > Ticket Discount Code Collection > List All Ticket Discount Codes")
def ticket_discount_code_get_list(transaction):
    """
    GET /events/1/discount-codes
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        discount_code = DiscountCodeFactory()
        db.session.add(discount_code)
        db.session.commit()


@hooks.before("Discount Codes > Ticket Discount Code Collection > Create Ticket Discount Code")
def ticket_discount_code_post(transaction):
    """
    POST /events/1/discount-codes
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
        db.session.commit()


@hooks.before("Discount Codes > Discount Code Detail > Discount Code Detail")
def discount_code_get_detail(transaction):
    """
    GET /discount-codes/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        discount_code = DiscountCodeFactory()
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
        discount_code = DiscountCodeFactory()
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
        discount_code = DiscountCodeFactory()
        db.session.add(discount_code)
        db.session.commit()


# ------------------------- Access Codes -------------------------
@hooks.before("Access Codes > Access Code Collection > List All Access Codes")
def access_code_get_list(transaction):
    """
    GET /events/1/access-codes
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        access_code = AccessCodeFactory()
        db.session.add(access_code)
        db.session.commit()


@hooks.before("Access Codes > Access Code Collection > Create Access Code")
def access_code_post(transaction):
    """
    POST /events/1/access-codes
    :param transaction:
    :return:
    """
    # Skip until docs for direct endpoints added
    transaction['skip'] = True

    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
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
def access_delete(transaction):
    """
    DELETE /access-codes/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        access_code = AccessCodeFactory()
        db.session.add(access_code)
        db.session.commit()


# ------------------------- Role Invites -------------------------
@hooks.before("Role Invites > Role Invites Collection > List All Role Invites")
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
    POST /events/1/role-invites
    :param transaction:
    :return:
    """
    # Skip until docs for direct endpoints added
    transaction['skip'] = True

    with stash['app'].app_context():
        event = EventFactoryBasic()
        db.session.add(event)
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


@hooks.before("Role Invites > Role Invite Details > Update Role Invite")
def role_invite_patch(transaction):
    """
    PATCH /role-invites/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        role_invite = RoleInviteFactory()
        db.session.add(role_invite)
        db.session.commit()


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
@hooks.before("Users Events Roles > Users Events Roles Collection > List All Users Events Roles")
def users_events_role_get_list(transaction):
    """
    GET /events/1/users-events-roles
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        users_events_role = UsersEventsRoleFactory()
        db.session.add(users_events_role)
        db.session.commit()


@hooks.before("Users Events Roles > Users Events Roles Collection > Create Users Events Role")
def users_events_role_post(transaction):
    """
    POST /events/1/users-events-roles
    :param transaction:
    :return:
    """
    # Skip until docs for direct endpoints added
    transaction['skip'] = True

    with stash['app'].app_context():
        event = EventFactoryBasic()
        role_invite = RoleInviteFactory()
        role = RoleFactory()
        user = UserFactory()
        db.session.add(event)
        db.session.add(role)
        db.session.add(user)
        role_invite.role_id = 1
        role_invite.event_id = 1
        db.session.add(role_invite)
        db.session.commit()


@hooks.before("Users Events Roles > Users Events Role Details > Users Events Role Details")
def users_events_role_get_detail(transaction):
    """
    GET /users-events-roles/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        users_events_role = UsersEventsRoleFactory()
        db.session.add(users_events_role)
        db.session.commit()


@hooks.before("Users Events Roles > Users Events Role Details > Update Users Events Role")
def users_events_role_patch(transaction):
    """
    PATCH /users-events-roles/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        users_events_role = UsersEventsRoleFactory()
        db.session.add(users_events_role)
        db.session.commit()


@hooks.before("Users Events Roles > Users Events Role Details > Delete Users Events Role")
def users_events_role_delete(transaction):
    """
    DELETE /users-events-roles/1
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        users_events_role = UsersEventsRoleFactory()
        db.session.add(users_events_role)
        db.session.commit()


# ------------------------- Upload -------------------------
@hooks.before("Upload > Image Upload > Upload an Image in temporary location")
def image_upload_post(transaction):
    """

    :param transaction:
    :return:
    """
    pass


@hooks.before("Upload > File Upload > Upload a File")
def file_upload_post(transaction):
    """

    :param transaction:
    :return:
    """
    transaction['skip'] = True


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
    pass


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
    pass


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


# ------------------------- Event Sub Topics -------------------------
@hooks.before("Event Sub Topics > Event Sub Topics Collection > List All Event Sub Topics")
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


@hooks.before("Event Sub Topics > Event Sub Topics Collection > Create Event Sub Topic")
def event_sub_topic_post(transaction):
    """
    POST /event-topics/1/event-sub-topics
    :param transaction:
    :return:
    """
    with stash['app'].app_context():
        event_topic = EventTopicFactory()
        db.session.add(event_topic)
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


# ------------------------- Custom Placeholders -------------------------
@hooks.before("Custom Placeholders > Custom Placeholders Collection > List All Event Custom Placeholders")
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


@hooks.before("Custom Placeholders > Custom Placeholders Collection > Create Custom Placeholder")
def custom_placeholder_post(transaction):
    """
    POST /custom-placeholders
    :param transaction:
    :return:
    """
    pass


@hooks.before("Custom Placeholders > Custom Placeholder Details > Custom Placeholder Details")
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


@hooks.before("Custom Placeholders > Custom Placeholder Details > Update Custom Placeholder")
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


@hooks.before("Custom Placeholders > Custom Placeholder Details > Delete Custom Placeholder")
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


@hooks.before("User Permissions > User Permission Collection > Create User Permission")
def user_permission_post(transaction):
    """
    POST /user-permissions
    :param transaction:
    :return:
    """
    pass


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
