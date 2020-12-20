from flask import Blueprint, jsonify

from app.api.helpers.errors import ForbiddenError
from app.api.helpers.permissions import jwt_required
from app.api.helpers.permission_manager import has_access
from app.models.event import Event
from app.models.role_invite import RoleInvite

role_invites_routes = Blueprint('role_invites_routes', __name__, url_prefix='/v1/role-invites')

@role_invites_routes.route(
    '/<int:role_invite_id>/resend-invite'
, methods=['POST'])
@jwt_required
def resend_invite(role_invite_id):
    role_invite = RoleInvite.query.get_or_404(role_invite_id)
    event = Event.query.filter_by(id=role_invite.event_id).first()
    if has_access('is_organizer', event_id=event.id):
        RoleInvite.send_invite_mail(role_invite)
        return jsonify(
            status=True,
            message="Resend invite successfully",
        )
    raise ForbiddenError({'source': ''}, "Organizer Access Required")
