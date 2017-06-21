import sys
import os.path as path
import dredd_hooks as hooks
import requests
sys.path.insert(1, path.abspath(path.join(__file__, "../..")))

from flask_migrate import Migrate, stamp
from flask import Flask
from app.models import db
from populate_db import populate_without_print
from app.helpers.data import DataManager
from app.factories.user_factory import UserFactory
from app.models.user import User

stash = {}
api_username = "open_event_test_user@fossasia.org"
api_password = "fossasia"
api_uri = "http://localhost:5000/auth/session"


@hooks.before_all
def before_all(transaction):
    app = Flask(__name__)
    app.config.from_object('config.TestingConfig')
    db.init_app(app)
    Migrate(app, db)
    stash['app'] = app
    stash['db'] = db


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


@hooks.before_each
def before_each(transaction):
    with stash['app'].app_context():
        db.engine.execute("drop schema if exists public cascade")
        db.engine.execute("create schema public")
        db.create_all()
        stamp()
        DataManager.create_super_admin(api_username, api_password)
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
        super_admin = User.query.filter_by(id=1).first()
        db.session.delete(super_admin)
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
    transaction['skip'] = True


@hooks.before("Events > Events Collection > Create Event")
def event_post(transaction):
    """
    POST /events
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Events > Event Details > Event Details")
def event_get_detail(transaction):
    """
    GET /events/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Events > Event Details > Update Event")
def event_patch(transaction):
    """
    PATCH /events/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Events > Event Details > Delete Event")
def event_delete(transaction):
    """
    DELETE /events/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Copyright > Event Copyright > Get Event Copyright")
def copyright_get_list(transaction):
    """
    GET /events/1/event-copyright
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Copyright > Event Copyright > Create Event Copyright")
def copyright_post(transaction):
    """
    POST /events/1/event-copyright
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Copyright > Event Copyright Details > Event Copyright Details")
def copyright_get_detail(transaction):
    """
    GET /event-copyright/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Copyright > Event Copyright Details > Update Event Copyright")
def copyright_patch(transaction):
    """
    PATCH /event-copyright/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Copyright > Event Copyright Details > Delete Event Copyright")
def copyright_delete(transaction):
    """
    DELETE /event-copyright/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Invoices > Event Invoices > Get Event Invoices")
def invoice_get_list(transaction):
    """
    GET /events/1/event-invoices
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Invoices > Event Invoices > Create Event Invoices")
def invoice_post(transaction):
    """
    POST /events/1/event-invoices
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Invoices > Event Invoices Details > Event Invoices Details")
def invoice_get_detail(transaction):
    """
    GET /event-invoices/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Invoices > Event Invoices Details > Update Event Invoices")
def invoice_patch(transaction):
    """
    PATCH /event-invoices/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Invoices > Event Invoices Details > Delete Event Invoices")
def invoice_delete(transaction):
    """
    DELETE /event-invoices/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Microlocations > Microlocation Collection > List All Microlocations")
def microlation_get_list(transaction):
    """
    GET /events/1/microlocations
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Microlocations > Microlocation Collection > Create Microlocation")
def microlocation_post(transaction):
    """
    POST /events/1/microlocations
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Microlocations > Microlocation Details > Mictolocation Details")
def microlation_get_detail(transaction):
    """
    GET /microlocations/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Microlocations > Microlocation Details > Update Microlocation")
def microlocation_patch(transaction):
    """
    PATCH /microlocations/1
    :param transcation:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Microlocations > Microlocation Details > Delete Microlocation")
def microlocation_delete(transaction):
    """
    DELETE /microlocations/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Sessions > Sessions Collection > List All Sessions")
def session_get_list(transaction):
    """
    GET /events/1/sessions
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Sessions > Sessions Collection > Create Sessions")
def session_post(transaction):
    """
    POST /events/1/sessions
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Sessions > Sessions Details > Session Details")
def session_get_detail(transaction):
    """
    GET /sessions/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Sessions > Sessions Details > Update Session")
def session_patch(transaction):
    """
    PATCH /sessions/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Sessions > Sessions Details > Delete Session")
def session_delete(transaction):
    """
    DELETE /sessions/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Session Type > Session Type Collection > List All Session Types")
def session_type_get_list(transaction):
    """
    GET /events/1/session-types
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Session Type > Session Type Collection > Create Session Type")
def session_type_post(transaction):
    """
    POST /events/1/session-types
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Session Type > Session Type Details > Session Type Details")
def session_type_get_detail(transaction):
    """
    GET /session-types/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Session Type > Session Type Details > Update Session Type")
def session_type_patch(transaction):
    """
    PATCH /session-types/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Session Type > Session Type Details > Delete Session Type")
def session_type_delete(transaction):
    """
    DELETE /session-types/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Social Links > Social Links Collection > List All Social Links")
def social_link_get_list(transaction):
    """
    GET /events/1/social-links
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Social Links > Social Links Collection > Create Social Link")
def social_link_post(transaction):
    """
    POST /events/1/social-links
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Social Links > Social Links > Social Link Detail")
def social_link_get_detail(transaction):
    """
    GET /social-links/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Social Links > Social Links > Update Social Link")
def social_link_patch(transaction):
    """
    PATCH /social-links/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Social Links > Social Links > Delete Social Link")
def social_link_delete(transaction):
    """
    DELETE /social-links/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Speakers Calls > Create Speakers Call for an Event > Create Speakers Call")
def speakers_call_post(transaction):
    """
    POST /events/1/speakers-calls
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Speakers Calls > Speakers Call Details > Speakers Call Details")
@hooks.before("Speakers Calls > Get Speakers Call for an Event > Get Speakers Call")
def speakers_call_get_detail(transaction):
    """
    GET /v1/events/1/speakers-call
    GET /speakers-calls/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Speakers Calls > Speakers Call Details > Update Speakers Call")
def speakers_call_patch(transaction):
    """
    PATCH /speakers-calls/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Speakers Calls > Speakers Call Details > Delete Speakers Call")
def speakers_call_delete(transaction):
    """
    DELETE /speakers-calls/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Sponsors > Sponsors Collection > List All Sponsors")
def sponsor_get_list(transaction):
    """
    GET /events/1/sponsors
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Sponsors > Sponsors Collection > Create Sponsor")
def sponsor_post(transaction):
    """
    POST /events/1/sponsors
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Sponsors > Sponsor Details > Sponsor Details")
def sponsor_get_detail(transaction):
    """
    GET /sponsors/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Sponsors > Sponsor Details > Update Sponsor")
def sponsor_patch(transaction):
    """
    PATCH /sponsors/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Sponsors > Sponsor Details > Delete Sponsor")
def sponsor_delete(transaction):
    """
    DELETE /sponsors/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Tax > Tax Collection > List All Tax Records")
def tax_get_list(transaction):
    """
    GET /events/1/tax
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Tax > Tax Collection > Create Tax")
def tax_get_list(transaction):
    """
    GET /tax/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Tax > Tax Details > Update Tax")
def tax_patch(transaction):
    """
    PATCH /tax/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Tax > Tax Details > Delete Tax")
def tax_delete(transaction):
    """
    DELETE /tax/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Tickets > Tickets Collection > List All Tickets")
def ticket_get_list(transaction):
    """
    GET /events/1/tickets
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Tickets > Tickets Collection > Create Ticket")
def ticket_post(transaction):
    """
    POST /events/1/tickets
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Tickets > Ticket Details > Ticket Details")
def ticket_get_detail(transaction):
    """
    GET /tickets/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Tickets > Ticket Details > Update Ticket")
def ticket_patch(transaction):
    """
    PATCH /tickets/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Tickets > Ticket Details > Delete Ticket")
def ticket_delete(transaction):
    """
    DELETE /tickets/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Tracks > Tracks Collection > List All Tracks")
def track_get_list(transaction):
    """
    GET /events/1/tracks
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Tracks > Tracks Collection > Create Track")
def track_post(transaction):
    """
    POST /events/1/tracks
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Tracks > Track Detail > Get Details")
def track_get_detail(transaction):
    """
    GET /tracks/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Tracks > Track Detail > Delete Track")
def track_delete(transaction):
    """
    DELETE /tracks/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Notifications > Notifications Collection > List All Notifications")
def notification_get_list(transaction):
    """
    GET /users/1/notifications
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Notifications > Notifications Collection > Create Notificaiton")
def notification_post(transaction):
    """
    POST /users/1/notifications
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Notifications > Notification Detail > Notification Detail")
def notification_get_detail(transaction):
    """
    GET /notifications/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Notifications > Notification Detail > Update Notification")
def notification_patch(transaction):
    """
    PATCH /notifications/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Notifications > Notification Detail > Delete Notification")
def notification_delete(transaction):
    """
    DELETE /notifications/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Image Size > Image Size Collection > List Image Sizes")
def image_size_get_list(transaction):
    """
    GET /image-sizes
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Image Size > Image Size Collection > Create Image Size")
def image_size_post(transaction):
    """
    POST /image-sizes
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Image Size > Image Size Details > Get Image Size Details")
def image_size_patch(transaction):
    """
    GET /image-sizes/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Image Size > Image Size Details > Update Image Size")
def image_size_patch(transaction):
    """
    PATCH /image-sizes/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Image Size > Image Size Details > Delete Image Size")
def image_size_delete(transaction):
    """
    DELETE /image-sizes/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Pages > Page Collection > Page Sizes")
def page_get_detail(transaction):
    """
    GET /pages
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Pages > Page Collection > Create Page")
def page_post(transaction):
    """
    POST /pages
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Pages > Page Details > Get Page Details")
def page_get_detail(transaction):
    """
    GET /pages/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Pages > Page Details > Update Page")
def page_patch(transaction):
    """
    PATCH /pages/1
    :param transation:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Pages > Page Details > Delete Page")
def page_delete(transaction):
    """
    DELETE /pages/1
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Settings > Settings Details > Show Settings")
def settings_get_list(transaction):
    """
    GET /settings
    :param transaction:
    :return:
    """
    transaction['skip'] = True


@hooks.before("Settings > Settings Details > Update Settings")
def settings_post(transaction):
    """
    POST /settings
    :param transaction:
    :return:
    """
    transaction['skip'] = True
