import base64

from flask import Blueprint, abort, make_response
from flask import request, jsonify

from app.api.helpers.db import save_to_db

from app.api.helpers.utilities import get_serializer
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
        save_to_db(user)

    return jsonify({
        "id": user.id,
        "email": user.email,
        "name": user.name if user.get('name') else None
    })
