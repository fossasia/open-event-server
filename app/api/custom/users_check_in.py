from flask import Blueprint, request
from flask.helpers import send_from_directory

from app.api.helpers.permissions import jwt_required
from app.api.helpers.user_check_in import export_csv

users_check_in_routes = Blueprint('users_check_in_routes', __name__, url_prefix='/v1')


@users_check_in_routes.route('/export/user-check-in/csv', methods=['POST'])
@jwt_required
def export_user_check_in_csv():
    """Export user check-in data as CSV."""
    file_path = export_csv(request.json)
    return send_from_directory('../', file_path, as_attachment=True)
