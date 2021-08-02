import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import current_user

from app.api.helpers.db import save_to_db
from app.api.helpers.errors import ConflictError, ForbiddenError, NotFoundError
from app.api.helpers.permissions import jwt_required
from app.models.user import User
from app.models.users_groups_role import UsersGroupsRoles

logger = logging.getLogger(__name__)

users_groups_roles_routes = Blueprint(
    'users_groups_roles_routes', __name__, url_prefix='/v1/users-groups-roles'
)


@users_groups_roles_routes.route('/accept-invite', methods=['POST'])
@jwt_required
def accept_invite():
    token = request.json['data']['token']

    users_groups_role = UsersGroupsRoles.query.filter_by(token=token).first()
    if not users_groups_role:
        raise NotFoundError(
            {'pointer': 'users_groups_role'}, 'Users Group Role Not Found'
        )
    if users_groups_role.accepted:
        raise ConflictError(
            {'pointer': 'users_groups_role'}, 'Invitation is already accepted'
        )

    user = User.query.filter_by(email=users_groups_role.email).first()
    if not user:
        raise NotFoundError(
            {'pointer': 'user'}, 'User corresponding to Users Group Role not Found'
        )
    if user != current_user:
        raise ForbiddenError({'pointer': 'user'}, 'current user is not invitee')

    role = users_groups_role.role

    if not users_groups_role.user:
        users_groups_role.user = user
    users_groups_role.accepted = True
    save_to_db(users_groups_role, 'Users Groups Role Accepted')

    if not user.is_verified:
        user.is_verified = True
        save_to_db(user, 'User verified')

    return jsonify(
        {
            "email": user.email,
            "group": users_groups_role.group_id,
            "name": user.fullname,
            "role": role.name,
        }
    )
