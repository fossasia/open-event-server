import jwt
from flask import Blueprint, current_app, request

from app.api.helpers.permissions import jwt_required

users_routes = Blueprint('users_routes', __name__, url_prefix='/v1/users')


@users_routes.route('/user-details/get-user-id', methods=['GET'])
@jwt_required
def get_user_id():
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
        print(data)
        return {"user_id": data["identity"]}, 200
    except Exception:
        return {"message": "Can't get user id!", "data": None}, 500
