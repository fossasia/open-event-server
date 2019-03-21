import base64
import random
import string

import requests
from flask import request, jsonify, make_response, Blueprint
from flask_jwt import current_identity as current_user, jwt_required
from sqlalchemy.orm.exc import NoResultFound

from app import get_settings
from app.api.helpers.db import save_to_db, get_count
from app.api.helpers.errors import UnprocessableEntityError, NotFoundError, BadRequestError
from app.api.helpers.files import make_frontend_url
from app.api.helpers.mail import send_email_with_action, \
    send_email_confirmation
from app.api.helpers.notification import send_notification_with_action
from app.api.helpers.third_party_auth import GoogleOAuth, FbOAuth, TwitterOAuth, InstagramOAuth
from app.api.helpers.utilities import get_serializer, str_generator
from app.models import db
from app.models.mail import PASSWORD_RESET, PASSWORD_CHANGE, \
    USER_REGISTER_WITH_PASSWORD, PASSWORD_RESET_AND_VERIFY
from app.models.notification import PASSWORD_CHANGE as PASSWORD_CHANGE_NOTIF
from app.models.user import User

auth_routes = Blueprint('auth', __name__, url_prefix='/v1/auth')


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
    token = base64.b64decode(request.json['data']['token'])
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
def reset_password_post():
    try:
        email = request.json['data']['email']
    except TypeError:
        return BadRequestError({'source': ''}, 'Bad Request Error').respond()

    try:
        user = User.query.filter_by(email=email).one()
    except NoResultFound:
        return NotFoundError({'source': ''}, 'User not found').respond()
    else:
        link = make_frontend_url('/reset-password', {'token': user.reset_password})
        if user.was_registered_with_order:
            send_email_with_action(user, PASSWORD_RESET_AND_VERIFY, app_name=get_settings()['app_name'], link=link)
        else:
            send_email_with_action(user, PASSWORD_RESET, app_name=get_settings()['app_name'], link=link)

    return make_response(jsonify(message="Email Sent"), 200)


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
        if user.was_registered_with_order:
            user.is_verified = True
        save_to_db(user)

    return jsonify({
        "id": user.id,
        "email": user.email,
        "name": user.fullname if user.fullname else None
    })


@auth_routes.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    old_password = request.json['data']['old-password']
    new_password = request.json['data']['new-password']

    try:
        user = User.query.filter_by(id=current_user.id).one()
    except NoResultFound:
        return NotFoundError({'source': ''}, 'User Not Found').respond()
    else:
        if user.is_correct_password(old_password):
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
            return BadRequestError({'source': ''}, 'Wrong Password').respond()

    return jsonify({
        "id": user.id,
        "email": user.email,
        "name": user.fullname if user.fullname else None,
        "password-changed": True
    })
