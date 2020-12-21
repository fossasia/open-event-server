from flask import Blueprint, jsonify

from app.api.helpers.permissions import jwt_required
from app.models.role_invite import RoleInvite

role_invites_routes = Blueprint(
    'role_invites_routes', __name__, url_prefix='/v1/role-invites'
)


@role_invites_routes.route('/<int:role_invite_id>/resend-invite', methods=['POST'])
@jwt_required
def resend_invite(role_invite_id):
    """
    Resend mail to invitee
    :param role_invite_id:
    :return: JSON response if the email was successfully sent
    """
    role_invite = RoleInvite.query.get_or_404(role_invite_id)
    role_invite.send_invite()
    return jsonify(
        success=True,
        message="Invite resent successfully",
    )
