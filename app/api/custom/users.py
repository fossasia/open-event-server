import jwt
from flask import Blueprint, current_app, request

from app.api.helpers.permissions import jwt_required

users_routes = Blueprint('users_routes', __name__, url_prefix='/v1/users')


@users_routes.route('/user-details/get-user-id', methods=['GET'])
@jwt_required
def get_user_id():
    """
    Get user id from token
    """
    token = None
    if "Authorization" in request.headers:
        token = request.headers["Authorization"].split(" ")[1]
    if not token:
        return {
            "message": "Authentication Token is missing!",
            "data": None,
            "error": "Unauthorized",
        }, 401
    try:
        data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        if not data.get('identity', False):
            return {"message": "Can't get user id!", "data": None}, 404
        return {"user_id": data["identity"]}, 200
    except UnicodeDecodeError:
        return {"message": "Can't get user id!", "data": None}, 500
