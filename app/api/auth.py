import base64
import logging
import random
import string
from datetime import timedelta
from functools import wraps

import requests
from flask import Blueprint, jsonify, make_response, request, send_file
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    current_user,
    fresh_jwt_required,
    get_jwt_identity,
    jwt_refresh_token_required,
    jwt_required,
    set_refresh_cookies,
    unset_jwt_cookies,
)
from healthcheck import EnvironmentDump
from sqlalchemy.orm.exc import NoResultFound

from app.api.helpers.auth import AuthManager, blacklist_token
from app.api.helpers.db import get_count, save_to_db
from app.api.helpers.errors import (
    BadRequestError,
    NotFoundError,
    UnprocessableEntityError,
)
from app.api.helpers.files import make_frontend_url
from app.api.helpers.jwt import jwt_authenticate
from app.api.helpers.mail import send_email_confirmation, send_email_with_action
from app.api.helpers.notification import send_notification_with_action
from app.api.helpers.third_party_auth import (
    FbOAuth,
    GoogleOAuth,
    InstagramOAuth,
    TwitterOAuth,
)
from app.api.helpers.utilities import get_serializer, str_generator
from app.extensions.limiter import limiter
from app.models import db
from app.models.mail import PASSWORD_CHANGE, PASSWORD_RESET, PASSWORD_RESET_AND_VERIFY
from app.models.notification import PASSWORD_CHANGE as PASSWORD_CHANGE_NOTIF
from app.models.user import User
from app.settings import get_settings

logger = logging.getLogger(__name__)
authorised_blueprint = Blueprint('authorised_blueprint', __name__, url_prefix='/')
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
        return make_response(jsonify(message="No support for {}".format(provider)), 404)

    client_id = provider_class.get_client_id()
    if not client_id:
        return make_response(
            jsonify(
                message="{} client id is not configured on the server".format(provider)
            ),
            404,
        )

    url = (
        provider_class.get_auth_uri()
        + '?client_id='
        + client_id
        + '&redirect_uri='
        + provider_class.get_redirect_uri()
    )
    return make_response(jsonify(url=url), 200)


@auth_routes.route('/oauth/token/<provider>', methods=['GET'])
def get_token(provider):
    if provider == 'facebook':
        provider_class = FbOAuth()
        payload = {
            'grant_type': 'client_credentials',
            'client_id': provider_class.get_client_id(),
            'client_secret': provider_class.get_client_secret(),
        }
    elif provider == 'google':
        provider_class = GoogleOAuth()
        payload = {
            'client_id': provider_class.get_client_id(),
            'client_secret': provider_class.get_client_secret(),
        }
    elif provider == 'twitter':
        provider_class = TwitterOAuth()
        payload = {
            'client_id': provider_class.get_client_id(),
            'client_secret': provider_class.get_client_secret(),
        }
    elif provider == 'instagram':
        provider_class = InstagramOAuth()
        payload = {
            'client_id': provider_class.get_client_id(),
            'client_secret': provider_class.get_client_secret(),
        }
    else:
        return make_response(jsonify(message="No support for {}".format(provider)), 200)
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
            'code': request.args.get('code'),
        }
        if not payload['client_id'] or not payload['client_secret']:
            raise NotImplementedError({'source': ''}, 'Facebook Login Not Configured')
        access_token = requests.get(
            'https://graph.facebook.com/v3.0/oauth/access_token', params=payload
        ).json()
        payload_details = {
            'input_token': access_token['access_token'],
            'access_token': provider_class.get_client_id()
            + '|'
            + provider_class.get_client_secret(),
        }
        details = requests.get(
            'https://graph.facebook.com/debug_token', params=payload_details
        ).json()
        user_details = requests.get(
            'https://graph.facebook.com/v3.0/' + details['data']['user_id'],
            params={
                'access_token': access_token['access_token'],
                'fields': 'first_name, last_name, email',
            },
        ).json()

        if get_count(db.session.query(User).filter_by(email=user_details['email'])) > 0:
            user = db.session.query(User).filter_by(email=user_details['email']).one()
            if not user.facebook_id:
                user.facebook_id = user_details['id']
                user.facebook_login_hash = random.getrandbits(128)
                save_to_db(user)
            return make_response(
                jsonify(
                    user_id=user.id, email=user.email, oauth_hash=user.facebook_login_hash
                ),
                200,
            )

        user = User()
        user.first_name = user_details['first_name']
        user.last_name = user_details['last_name']
        user.facebook_id = user_details['id']
        user.facebook_login_hash = random.getrandbits(128)
        user.password = ''.join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits)
            for _ in range(8)
        )
        if user_details['email']:
            user.email = user_details['email']

        save_to_db(user)
        return make_response(
            jsonify(
                user_id=user.id, email=user.email, oauth_hash=user.facebook_login_hash
            ),
            200,
        )

    elif provider == 'google':
        provider_class = GoogleOAuth()
        payload = {
            'client_id': provider_class.get_client_id(),
            'client_secret': provider_class.get_client_secret(),
        }
    elif provider == 'twitter':
        provider_class = TwitterOAuth()
        payload = {
            'client_id': provider_class.get_client_id(),
            'client_secret': provider_class.get_client_secret(),
        }
    elif provider == 'instagram':
        provider_class = InstagramOAuth()
        payload = {
            'client_id': provider_class.get_client_id(),
            'client_secret': provider_class.get_client_secret(),
        }
    else:
        return make_response(jsonify(message="No support for {}".format(provider)), 200)
    response = requests.post(provider_class.get_token_uri(), params=payload)
    return make_response(jsonify(token=response.json()), 200)


@auth_routes.route('/verify-email', methods=['POST'])
def verify_email():
    try:
        token = base64.b64decode(request.json['data']['token'])
    except base64.binascii.Error:
        raise BadRequestError({'source': ''}, 'Invalid Token')
    s = get_serializer()

    try:
        data = s.loads(token)
    except Exception:
        raise BadRequestError({'source': ''}, 'Invalid Token')

    try:
        user = User.query.filter_by(email=data[0]).one()
    except Exception:
        raise BadRequestError({'source': ''}, 'Invalid Token')
    else:
        user.is_verified = True
        save_to_db(user)
        return make_response(jsonify(message="Email Verified"), 200)


@auth_routes.route('/resend-verification-email', methods=['POST'])
def resend_verification_email():
    try:
        email = request.json['data']['email']
    except TypeError:
        raise BadRequestError({'source': ''}, 'Bad Request Error')

    try:
        user = User.query.filter_by(email=email).one()
    except NoResultFound:
        raise UnprocessableEntityError(
            {'source': ''}, 'User with email: ' + email + ' not found.'
        )
    else:
        serializer = get_serializer()
        hash_ = str(
            base64.b64encode(
                str(serializer.dumps([user.email, str_generator()])).encode()
            ),
            'utf-8',
        )
        link = make_frontend_url('/verify'.format(id=user.id), {'token': hash_})
        send_email_confirmation(user.email, link)

        return make_response(jsonify(message="Verification email resent"), 200)


@auth_routes.route('/reset-password', methods=['POST'])
@limiter.limit(
    '3/hour',
    key_func=lambda: request.json['data']['email'],
    error_message='Limit for this action exceeded',
)
@limiter.limit('1/minute', error_message='Limit for this action exceeded')
def reset_password_post():
    try:
        email = request.json['data']['email']
    except TypeError:
        raise BadRequestError({'source': ''}, 'Bad Request Error')

    try:
        user = User.query.filter_by(email=email).one()
    except NoResultFound:
        logger.info('Tried to reset password not existing email %s', email)
    else:
        link = make_frontend_url('/reset-password', {'token': user.reset_password})
        if user.was_registered_with_order:
            send_email_with_action(
                user,
                PASSWORD_RESET_AND_VERIFY,
                app_name=get_settings()['app_name'],
                link=link,
            )
        else:
            send_email_with_action(
                user,
                PASSWORD_RESET,
                app_name=get_settings()['app_name'],
                link=link,
                token=user.reset_password,
            )

    return make_response(
        jsonify(
            message="If your email was registered with us, you'll get an \
                         email with reset link shortly",
            email=email,
        ),
        200,
    )


@auth_routes.route('/reset-password', methods=['PATCH'])
def reset_password_patch():
    token = request.json['data']['token']
    password = request.json['data']['password']

    try:
        user = User.query.filter_by(reset_password=token).one()
    except NoResultFound:
        raise NotFoundError({'source': ''}, 'User Not Found')
    else:
        user.password = password
        if not user.is_verified:
            user.is_verified = True
        save_to_db(user)

    return jsonify(
        {
            "id": user.id,
            "email": user.email,
            "name": user.fullname if user.fullname else None,
        }
    )


@auth_routes.route('/change-password', methods=['POST'])
@fresh_jwt_required
def change_password():
    old_password = request.json['data']['old-password']
    new_password = request.json['data']['new-password']

    try:
        user = User.query.filter_by(id=current_user.id).one()
    except NoResultFound:
        raise NotFoundError({'source': ''}, 'User Not Found')
    else:
        if user.is_correct_password(old_password):
            if user.is_correct_password(new_password):
                raise BadRequestError(
                    {'source': ''}, 'Old and New passwords must be different'
                )
            if len(new_password) < 8:
                raise BadRequestError(
                    {'source': ''}, 'Password should have minimum 8 characters'
                )
            user.password = new_password
            save_to_db(user)
            send_email_with_action(
                user, PASSWORD_CHANGE, app_name=get_settings()['app_name']
            )
            send_notification_with_action(
                user, PASSWORD_CHANGE_NOTIF, app_name=get_settings()['app_name']
            )
        else:
            raise BadRequestError(
                {'source': ''}, 'Wrong Password. Please enter correct current password.'
            )

    return jsonify(
        {
            "id": user.id,
            "email": user.email,
            "name": user.fullname if user.fullname else None,
            "password-changed": True,
        }
    )


def return_file(file_name_prefix, file_path, identifier):
    response = make_response(send_file(file_path))
    response.headers['Content-Disposition'] = 'attachment; filename=%s-%s.pdf' % (
        file_name_prefix,
        identifier,
    )
    return response


# Access for Environment details & Basic Auth Support
def requires_basic_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not AuthManager.check_auth_admin(auth.username, auth.password):
            return make_response(
                'Could not verify your access level for that URL.\n'
                'You have to login with proper credentials',
                401,
                {'WWW-Authenticate': 'Basic realm="Login Required"'},
            )
        return f(*args, **kwargs)

    return decorated


@authorised_blueprint.route('/environment')
@requires_basic_auth
def environment_details():
    envdump = EnvironmentDump(include_config=False)
    return envdump.dump_environment()
