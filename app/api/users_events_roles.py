from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.helpers.errors import ForbiddenError
from app.api.helpers.query import event_query
from app.api.schema.users_events_roles import UsersEventsRolesSchema
from app.models import db
from app.models.role_invite import RoleInvite
from app.models.users_events_role import UsersEventsRoles


class UsersEventsRolesList(ResourceList):
    """
    List and create users_events_roles
    """

    def query(self, view_kwargs):
        query_ = self.session.query(UsersEventsRoles)
        # users_events_roles under an event
        query_ = event_query(query_, view_kwargs)

        return query_

    view_kwargs = True
    decorators = (
        api.has_permission('is_coorganizer', fetch='event_id', model=UsersEventsRoles),
    )
    methods = ['GET']
    schema = UsersEventsRolesSchema
    data_layer = {
        'session': db.session,
        'model': UsersEventsRoles,
        'methods': {'query': query},
    }


class UsersEventsRolesDetail(ResourceDetail):
    """
    users_events_roles detail by id
    """

    def before_delete_object(self, users_events_roles, view_kwargs):
        role = users_events_roles.role
        if role:
            if role.name == "owner":
                raise ForbiddenError(
                    {'source': 'Role'},
                    'You cannot remove the owner of the event.',
                )
            RoleInvite.query.filter_by(
                event_id=users_events_roles.event_id,
                email=users_events_roles.user.email,
                role_id=role.id,
            ).delete(synchronize_session=False)

    methods = ['GET', 'PATCH', 'DELETE']
    decorators = (
        api.has_permission('is_coorganizer', fetch='event_id', model=UsersEventsRoles),
    )
    schema = UsersEventsRolesSchema
    data_layer = {
        'session': db.session,
        'model': UsersEventsRoles,
        'methods': {'before_delete_object': before_delete_object},
    }


class UsersEventsRolesRelationship(ResourceRelationship):
    """
    users_events_roles Relationship
    """

    methods = ['GET', 'PATCH']
    schema = UsersEventsRolesSchema
    data_layer = {'session': db.session, 'model': UsersEventsRoles}
