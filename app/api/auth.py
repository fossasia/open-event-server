import base64
from flask import request, jsonify, abort, make_response, Blueprint
from sqlalchemy.orm.exc import NoResultFound

from app import get_settings
from app.api.helpers.db import save_to_db
from app.api.helpers.files import make_frontend_url
from app.api.helpers.mail import send_email_with_action

from app.api.helpers.utilities import get_serializer
from app.models.mail import PASSWORD_RESET
from app.models.user import User

auth_routes = Blueprint('auth', __name__, url_prefix='/v1/auth')


@auth_routes.route('/verify-email', methods=['POST'])
def verify_email():
    token = base64.b64decode(request.json['data']['token'])
    s = get_serializer()

    try:
        data = s.loads(token)
    except Exception:
        return abort(
            make_response(jsonify(error="Invalid Token"), 400)
        )

    try:
        user = User.query.filter_by(email=data[0]).one()
    except Exception:
        return abort(
            make_response(jsonify(error="Invalid Token"), 400)
        )
    else:
        user.is_verified = True


@auth_routes.route('/reset-password', methods=['POST'])
def reset_password_post():
    email = request.json['data']['email']

    try:
        user = User.query.filter_by(email=email).one()
    except NoResultFound:
        return abort(
            make_response(jsonify(error="User not found"), 404)
        )
    else:
        link = make_frontend_url('/reset-password', {'token': user.reset_password})
        send_email_with_action(user, PASSWORD_RESET, app_name=get_settings()['app_name'], link=link)

    return make_response(jsonify(message="Email Sent"), 200)


@auth_routes.route('/reset-password', methods=['PATCH'])
def reset_password_patch():
    token = request.json['data']['token']
    password = request.json['data']['password']

    try:
        user = User.query.filter_by(reset_password=token).one()
    except NoResultFound:
        return abort(
            make_response(jsonify(error="User not found"), 404)
        )
    else:
        user.password = password
        save_to_db(user)

    return jsonify({
        "id": user.id,
        "email": user.email,
        "name": user.name if user.get('name') else None
    })
