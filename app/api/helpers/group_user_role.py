from app.models.group import Group
from app.models.role import Role
from app.models.users_groups_role import UsersGroupsRoles


def get_user_group_role(user_id, group_id):
    """
    Get the user role in a group
    :param user_id:
    :param group_id:
    :return:
    """
    group = Group.query.filter_by(id=group_id).first()
    user_group_role = UsersGroupsRoles.query.filter_by(
        user_id=user_id, group_id=group_id
    ).first()
    if group.user_id == user_id:
        return 'Owner'
    elif user_group_role:
        role = Role.query.filter_by(id=user_group_role.role_id).first()
        return role.name
    else:
        return 'Follower'
