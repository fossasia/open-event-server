import base64
import logging
import random
import string
from datetime import timedelta
from functools import wraps

import requests
from flask import request, jsonify, make_response, Blueprint, send_file
from flask_jwt_extended import (
    jwt_required, jwt_refresh_token_required,
    fresh_jwt_required, unset_jwt_cookies,
    current_user, create_access_token,
    create_refresh_token, set_refresh_cookies,
    get_jwt_identity)
from flask_limiter.util import get_remote_address
from healthcheck import EnvironmentDump
from flask_rest_jsonapi.exceptions import ObjectNotFound
from sqlalchemy.orm.exc import NoResultFound

from app import get_settings
from app import limiter
from app.api.helpers.db import save_to_db, get_count, safe_query
from app.api.helpers.auth import AuthManager, blacklist_token
from app.api.helpers.jwt import jwt_authenticate
from app.api.helpers.errors import ForbiddenError, UnprocessableEntityError, NotFoundError, BadRequestError
from app.api.helpers.files import make_frontend_url
from app.api.helpers.mail import send_email_to_attendees
from app.api.helpers.mail import send_email_with_action, \
    send_email_confirmation
from app.api.helpers.notification import send_notification_with_action
from app.api.helpers.order import create_pdf_tickets_for_holder, calculate_order_amount
from app.api.helpers.storage import UPLOAD_PATHS
from app.api.helpers.storage import generate_hash
from app.api.helpers.third_party_auth import GoogleOAuth, FbOAuth, TwitterOAuth, InstagramOAuth
from app.api.helpers.ticketing import TicketingManager
from app.api.helpers.utilities import get_serializer, str_generator
from app.api.helpers.permission_manager import has_access
from app.models import db
from app.models.mail import PASSWORD_RESET, PASSWORD_CHANGE, \
    PASSWORD_RESET_AND_VERIFY
from app.models.notification import PASSWORD_CHANGE as PASSWORD_CHANGE_NOTIF
from app.models.discount_code import DiscountCode
from app.models.order import Order
from app.models.user import User
from app.models.event_invoice import EventInvoice


logger = logging.getLogger(__name__)
authorised_blueprint = Blueprint('authorised_blueprint', __name__, url_prefix='/')
ticket_blueprint = Blueprint('ticket_blueprint', __name__, url_prefix='/v1')
auth_routes = Blueprint('auth', __name__, url_prefix='/v1/auth')


def authenticate(allow_refresh_token=False, existing_identity=None):
    data = request.get_json()
    username = data.get('email', data.get('username'))
    password = data.get('password')
    criterion = [username, password]

    if not all(criterion):
        return jsonify(error='username or password missing'), 400

    identity = jwt_authenticate(username, password)
    if not identity or (existing_identity and identity != existing_identity):
        # For fresh login, credentials should match existing user
        return jsonify(error='Invalid Credentials'), 401

    remember_me = data.get('remember-me')
    include_in_response = data.get('include-in-response')
    add_refresh_token = allow_refresh_token and remember_me

    expiry_time = timedelta(minutes=90) if add_refresh_token else None
    access_token = create_access_token(identity.id, fresh=True, expires_delta=expiry_time)
    response_data = {'access_token': access_token}

    if add_refresh_token:
        refresh_token = create_refresh_token(identity.id)
        if include_in_response:
            response_data['refresh_token'] = refresh_token

    response = jsonify(response_data)

    if add_refresh_token and not include_in_response:
        set_refresh_cookies(response, refresh_token)

    return response


@authorised_blueprint.route('/auth/session', methods=['POST'])
@auth_routes.route('/login', methods=['POST'])
def login():
    return authenticate(allow_refresh_token=True)


@auth_routes.route('/fresh-login', methods=['POST'])
@jwt_required
def fresh_login():
    return authenticate(existing_identity=current_user)


@auth_routes.route('/token/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh_token():
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user, fresh=False)
    return jsonify({'access_token': new_token})


@auth_routes.route('/logout', methods=['POST'])
def logout():
    response = jsonify({'success': True})
    unset_jwt_cookies(response)
    return response


@auth_routes.route('/blacklist', methods=['POST'])
@jwt_required
def blacklist_token_rquest():
    blacklist_token(current_user)
    return jsonify({'success': True})


@auth_routes.route('/oauth/<provider>', methods=['GET'])
def redirect_uri(provider):
    if provider == 'facebook':
        provider_class = FbOAuth()
    elif provider == 'google':
        provider_class = GoogleOAuth()
    elif provider == 'twitter':
        provider_class = TwitterOAuth()
    elif provider == 'instagram':
        provider_class = InstagramOAuth()
    else:
        return make_response(jsonify(
            message="No support for {}".format(provider)), 404)

    client_id = provider_class.get_client_id()
    if not client_id:
        return make_response(jsonify(
            message="{} client id is not configured on the server".format(provider)), 404)

    url = provider_class.get_auth_uri() + '?client_id=' + \
          client_id + '&redirect_uri=' + \
          provider_class.get_redirect_uri()
    return make_response(jsonify(url=url), 200)


@auth_routes.route('/oauth/token/<provider>', methods=['GET'])
def get_token(provider):
    if provider == 'facebook':
        provider_class = FbOAuth()
        payload = {
            'grant_type': 'client_credentials',
            'client_id': provider_class.get_client_id(),
            'client_secret': provider_class.get_client_secret()
        }
    elif provider == 'google':
        provider_class = GoogleOAuth()
        payload = {
            'client_id': provider_class.get_client_id(),
            'client_secret': provider_class.get_client_secret()
        }
    elif provider == 'twitter':
        provider_class = TwitterOAuth()
        payload = {
            'client_id': provider_class.get_client_id(),
            'client_secret': provider_class.get_client_secret()
        }
    elif provider == 'instagram':
        provider_class = InstagramOAuth()
        payload = {
            'client_id': provider_class.get_client_id(),
            'client_secret': provider_class.get_client_secret()
        }
    else:
        return make_response(jsonify(
            message="No support for {}".format(provider)), 200)
    response = requests.post(provider_class.get_token_uri(), params=payload)
    return make_response(jsonify(token=response.json()), 200)


@auth_routes.route('/oauth/login/<provider>', methods=['POST'])
def login_user(provider):
    if provider == 'facebook':
        provider_class = FbOAuth()
        payload = {
            'client_id': provider_class.get_client_id(),
            'redirect_uri': provider_class.get_redirect_uri(),
            'client_secret': provider_class.get_client_secret(),
            'code': request.args.get('code')
        }
        if not payload['client_id'] or not payload['client_secret']:
            raise NotImplementedError({'source': ''}, 'Facebook Login Not Configured')
        access_token = requests.get('https://graph.facebook.com/v3.0/oauth/access_token', params=payload).json()
        payload_details = {
            'input_token': access_token['access_token'],
            'access_token': provider_class.get_client_id() + '|' + provider_class.get_client_secret()
        }
        details = requests.get('https://graph.facebook.com/debug_token', params=payload_details).json()
        user_details = requests.get('https://graph.facebook.com/v3.0/' + details['data']['user_id'],
                                    params={'access_token': access_token['access_token'],
                                            'fields': 'first_name, last_name, email'}).json()

        if get_count(db.session.query(User).filter_by(email=user_details['email'])) > 0:
            user = db.session.query(User).filter_by(email=user_details['email']).one()
            if not user.facebook_id:
                user.facebook_id = user_details['id']
                user.facebook_login_hash = random.getrandbits(128)
                save_to_db(user)
            return make_response(
                jsonify(user_id=user.id, email=user.email, oauth_hash=user.facebook_login_hash), 200)

        user = User()
        user.first_name = user_details['first_name']
        user.last_name = user_details['last_name']
        user.facebook_id = user_details['id']
        user.facebook_login_hash = random.getrandbits(128)
        user.password = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))
        if user_details['email']:
            user.email = user_details['email']

        save_to_db(user)
        return make_response(jsonify(user_id=user.id, email=user.email, oauth_hash=user.facebook_login_hash),
                             200)

    elif provider == 'google':
        provider_class = GoogleOAuth()
        payload = {
            'client_id': provider_class.get_client_id(),
            'client_secret': provider_class.get_client_secret()
        }
    elif provider == 'twitter':
        provider_class = TwitterOAuth()
        payload = {
            'client_id': provider_class.get_client_id(),
            'client_secret': provider_class.get_client_secret()
        }
    elif provider == 'instagram':
        provider_class = InstagramOAuth()
        payload = {
            'client_id': provider_class.get_client_id(),
            'client_secret': provider_class.get_client_secret()
        }
    else:
        return make_response(jsonify(
            message="No support for {}".format(provider)), 200)
    response = requests.post(provider_class.get_token_uri(), params=payload)
    return make_response(jsonify(token=response.json()), 200)


@auth_routes.route('/verify-email', methods=['POST'])
def verify_email():
    try:
        token = base64.b64decode(request.json['data']['token'])
    except base64.binascii.Error:
        return BadRequestError({'source': ''}, 'Invalid Token').respond()
    s = get_serializer()

    try:
        data = s.loads(token)
    except Exception:
        return BadRequestError({'source': ''}, 'Invalid Token').respond()

    try:
        user = User.query.filter_by(email=data[0]).one()
    except Exception:
        return BadRequestError({'source': ''}, 'Invalid Token').respond()
    else:
        user.is_verified = True
        save_to_db(user)
        return make_response(jsonify(message="Email Verified"), 200)


@auth_routes.route('/resend-verification-email', methods=['POST'])
def resend_verification_email():
    try:
        email = request.json['data']['email']
    except TypeError:
        return BadRequestError({'source': ''}, 'Bad Request Error').respond()

    try:
        user = User.query.filter_by(email=email).one()
    except NoResultFound:
        return UnprocessableEntityError(
            {'source': ''}, 'User with email: ' + email + ' not found.').respond()
    else:
        serializer = get_serializer()
        hash_ = str(base64.b64encode(str(serializer.dumps(
            [user.email, str_generator()])).encode()), 'utf-8')
        link = make_frontend_url(
            '/verify'.format(id=user.id), {'token': hash_})
        send_email_confirmation(user.email, link)

        return make_response(jsonify(message="Verification email resent"), 200)


@auth_routes.route('/reset-password', methods=['POST'])
@limiter.limit(
    '3/hour', key_func=lambda: request.json['data']['email'], error_message='Limit for this action exceeded'
)
@limiter.limit(
    '1/minute', key_func=get_remote_address, error_message='Limit for this action exceeded'
)
def reset_password_post():
    try:
        email = request.json['data']['email']
    except TypeError:
        return BadRequestError({'source': ''}, 'Bad Request Error').respond()

    try:
        user = User.query.filter_by(email=email).one()
    except NoResultFound:
        logger.info('Tried to reset password not existing email %s', email)
    else:
        link = make_frontend_url('/reset-password', {'token': user.reset_password})
        if user.was_registered_with_order:
            send_email_with_action(user, PASSWORD_RESET_AND_VERIFY, app_name=get_settings()['app_name'], link=link)
        else:
            send_email_with_action(user, PASSWORD_RESET, app_name=get_settings()['app_name'], link=link, token=user.reset_password)

    return make_response(jsonify(message="If your email was registered with us, you'll get an \
                         email with reset link shortly", email=email), 200)


@auth_routes.route('/reset-password', methods=['PATCH'])
def reset_password_patch():
    token = request.json['data']['token']
    password = request.json['data']['password']

    try:
        user = User.query.filter_by(reset_password=token).one()
    except NoResultFound:
        return NotFoundError({'source': ''}, 'User Not Found').respond()
    else:
        user.password = password
        if not user.is_verified:
            user.is_verified = True
        save_to_db(user)

    return jsonify({
        "id": user.id,
        "email": user.email,
        "name": user.fullname if user.fullname else None
    })


@auth_routes.route('/change-password', methods=['POST'])
@fresh_jwt_required
def change_password():
    old_password = request.json['data']['old-password']
    new_password = request.json['data']['new-password']

    try:
        user = User.query.filter_by(id=current_user.id).one()
    except NoResultFound:
        return NotFoundError({'source': ''}, 'User Not Found').respond()
    else:
        if user.is_correct_password(old_password):
            if user.is_correct_password(new_password):
                return BadRequestError({'source': ''},
                                       'Old and New passwords must be different').respond()
            if len(new_password) < 8:
                return BadRequestError({'source': ''},
                                       'Password should have minimum 8 characters').respond()
            user.password = new_password
            save_to_db(user)
            send_email_with_action(user, PASSWORD_CHANGE,
                                   app_name=get_settings()['app_name'])
            send_notification_with_action(user, PASSWORD_CHANGE_NOTIF,
                                          app_name=get_settings()['app_name'])
        else:
            return BadRequestError({'source': ''}, 'Wrong Password. Please enter correct current password.').respond()

    return jsonify({
        "id": user.id,
        "email": user.email,
        "name": user.fullname if user.fullname else None,
        "password-changed": True
    })


def return_file(file_name_prefix, file_path, identifier):
    response = make_response(send_file(file_path))
    response.headers['Content-Disposition'] = 'attachment; filename=%s-%s.pdf' % (file_name_prefix, identifier)
    return response


@ticket_blueprint.route('/tickets/<string:order_identifier>')
@jwt_required
def ticket_attendee_authorized(order_identifier):
    if current_user:
        try:
            order = Order.query.filter_by(identifier=order_identifier).first()
        except NoResultFound:
            return NotFoundError({'source': ''}, 'This ticket is not associated with any order').respond()
        if current_user.can_download_tickets(order):
            key = UPLOAD_PATHS['pdf']['tickets_all'].format(identifier=order_identifier)
            file_path = '../generated/tickets/{}/{}/'.format(key, generate_hash(key)) + order_identifier + '.pdf'
            try:
                return return_file('ticket', file_path, order_identifier)
            except FileNotFoundError:
                create_pdf_tickets_for_holder(order)
                return return_file('ticket', file_path, order_identifier)
        else:
            return ForbiddenError({'source': ''}, 'Unauthorized Access').respond()
    else:
        return ForbiddenError({'source': ''}, 'Authentication Required to access ticket').respond()


@ticket_blueprint.route('/orders/invoices/<string:order_identifier>')
@jwt_required
def order_invoices(order_identifier):
    if current_user:
        try:
            order = Order.query.filter_by(identifier=order_identifier).first()
        except NoResultFound:
            return NotFoundError({'source': ''}, 'Order Invoice not found').respond()
        if current_user.can_download_tickets(order):
            key = UPLOAD_PATHS['pdf']['order'].format(identifier=order_identifier)
            file_path = '../generated/invoices/{}/{}/'.format(key, generate_hash(key)) + order_identifier + '.pdf'
            try:
                return return_file('invoice', file_path, order_identifier)
            except FileNotFoundError:
                create_pdf_tickets_for_holder(order)
                return return_file('invoice', file_path, order_identifier)
        else:
            return ForbiddenError({'source': ''}, 'Unauthorized Access').respond()
    else:
        return ForbiddenError({'source': ''}, 'Authentication Required to access Invoice').respond()


@ticket_blueprint.route('/events/invoices/<string:invoice_identifier>')
@jwt_required
def event_invoices(invoice_identifier):
    if not current_user:
        return ForbiddenError({'source': ''}, 'Authentication Required to access Invoice').respond()
    try:
        event_invoice = EventInvoice.query.filter_by(identifier=invoice_identifier).first()
        event_id = event_invoice.event_id
    except NoResultFound:
        return NotFoundError({'source': ''}, 'Event Invoice not found').respond()
    if not current_user.is_organizer(event_id) and not current_user.is_staff:
        return ForbiddenError({'source': ''}, 'Unauthorized Access').respond()
    key = UPLOAD_PATHS['pdf']['event_invoices'].format(identifier=invoice_identifier)
    file_path = '../generated/invoices/{}/{}/'.format(key, generate_hash(key)) + invoice_identifier + '.pdf'
    try:
        return return_file('event-invoice', file_path, invoice_identifier)
    except FileNotFoundError:
        raise ObjectNotFound({'source': ''},
                             "The Event Invoice isn't available at the moment. \
                             Invoices are usually issued on the 1st of every month")


# Access for Environment details & Basic Auth Support
def requires_basic_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not AuthManager.check_auth_admin(auth.username, auth.password):
            return make_response('Could not verify your access level for that URL.\n'
                                 'You have to login with proper credentials', 401,
                                 {'WWW-Authenticate': 'Basic realm="Login Required"'})
        return f(*args, **kwargs)
    return decorated


@authorised_blueprint.route('/environment')
@requires_basic_auth
def environment_details():
    envdump = EnvironmentDump(include_config=False)
    return envdump.dump_environment()


@ticket_blueprint.route('/orders/resend-email', methods=['POST'])
@limiter.limit(
    '5/minute', key_func=lambda: request.json['data']['user'], error_message='Limit for this action exceeded'
)
@limiter.limit(
    '60/minute', key_func=get_remote_address, error_message='Limit for this action exceeded'
)
def resend_emails():
    """
    Sends confirmation email for pending and completed orders on organizer request
    :param order_identifier:
    :return: JSON response if the email was succesfully sent
    """
    order_identifier = request.json['data']['order']
    order = safe_query(db, Order, 'identifier', order_identifier, 'identifier')
    if (has_access('is_coorganizer', event_id=order.event_id)):
        if order.status == 'completed' or order.status == 'placed':
            # fetch tickets attachment
            order_identifier = order.identifier
            key = UPLOAD_PATHS['pdf']['tickets_all'].format(identifier=order_identifier)
            ticket_path = 'generated/tickets/{}/{}/'.format(key, generate_hash(key)) + order_identifier + '.pdf'
            key = UPLOAD_PATHS['pdf']['order'].format(identifier=order_identifier)
            invoice_path = 'generated/invoices/{}/{}/'.format(key, generate_hash(key)) + order_identifier + '.pdf'

            # send email.
            send_email_to_attendees(order=order, purchaser_id=current_user.id, attachments=[ticket_path, invoice_path])
            return jsonify(status=True, message="Verification emails for order : {} has been sent succesfully".
                           format(order_identifier))
        else:
            return UnprocessableEntityError({'source': 'data/order'},
                                            "Only placed and completed orders have confirmation").respond()
    else:
        return ForbiddenError({'source': ''}, "Co-Organizer Access Required").respond()


@ticket_blueprint.route('/orders/calculate-amount', methods=['POST'])
@jwt_required
def calculate_amount():
    data = request.get_json()
    tickets = data['tickets']
    discount_code = None
    if 'discount-code' in data:
        discount_code_id = data['discount-code']
        discount_code = safe_query(db, DiscountCode, 'id', discount_code_id, 'id')
        if not TicketingManager.match_discount_quantity(discount_code, tickets, None):
            return UnprocessableEntityError({'source': 'discount-code'}, 'Discount Usage Exceeded').respond()

    return jsonify(calculate_order_amount(tickets, discount_code))
