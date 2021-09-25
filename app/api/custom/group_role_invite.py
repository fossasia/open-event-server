from flask import Blueprint, jsonify

from app.api.helpers.permissions import jwt_required
from app.models.users_groups_role import UsersGroupsRoles

group_role_invites_routes = Blueprint(
    'group_role_invites_routes', __name__, url_prefix='/v1/group-role-invites'
)


@group_role_invites_routes.route(
    '/<int:group_role_invite_id>/resend-invite', methods=['POST']
)
@jwt_required
def resend_invite(group_role_invite_id):
    """
    Resend mail to invitee
    :param group_role_invite_id:
    :return: JSON response if the email was successfully sent
    """
    group_role_invite = UsersGroupsRoles.query.get_or_404(group_role_invite_id)
    group_role_invite.send_invite()
    return jsonify(
        success=True,
        message="Invite resent successfully",
    )
