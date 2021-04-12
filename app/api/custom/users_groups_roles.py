import logging

from flask import Blueprint, jsonify, request

from app.api.helpers.db import save_to_db
from app.api.helpers.errors import NotFoundError, UnprocessableEntityError
from app.models.group import Group
from app.models.role import Role
from app.models.user import User
from app.models.users_groups_role import UsersGroupsRoles

logger = logging.getLogger(__name__)

users_groups_roles_routes = Blueprint(
    'users_groups_roles_routes', __name__, url_prefix='/v1/users-groups-roles'
)


@users_groups_roles_routes.route('/accept-invite', methods=['POST'])
def accept_invite():
    token = request.json['data']['token']

    users_groups_role = UsersGroupsRoles.query.filter_by(token=token).first()
    if not users_groups_role:
        raise NotFoundError({'source': ''}, 'Users Group Role Not Found')
    if users_groups_role.accepted:
        raise UnprocessableEntityError(
            {'parameter': ''}, 'Invitation is already accepted'
        )

    user = User.query.filter_by(email=users_groups_role.email).first()
    if not user:
        raise NotFoundError(
            {'source': ''}, 'User corresponding to Users Group Role not Found'
        )

    role = Role.query.filter_by(id=users_groups_role.role_id).first()
    if not role:
        raise NotFoundError(
            {'source': ''}, 'Role corresponding to Users Group Role not Found'
        )

    group = Group.query.filter_by(id=users_groups_role.group_id).first()
    if not group:
        raise NotFoundError(
            {'source': ''}, 'Group corresponding to Users Group Role not Found'
        )

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
            "name": user.fullname if user.fullname else None,
            "role": role.name,
        }
    )
