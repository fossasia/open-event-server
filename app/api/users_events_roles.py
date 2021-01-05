from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.helpers.query import event_query
from app.api.schema.users_events_roles import UsersEventsRolesSchema
from app.models import db
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
        api.has_permission('is_coorganizer', fetch='event_id', fetch_as="event_id"),
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

    decorators = (api.has_permission('is_coorganizer', methods="GET,PATCH,DELETE"),)
    methods = ['GET', 'PATCH', 'DELETE']
    schema = UsersEventsRolesSchema
    data_layer = {'session': db.session, 'model': UsersEventsRoles}


class UsersEventsRolesRelationship(ResourceRelationship):
    """
    users_events_roles Relationship
    """

    methods = ['GET', 'PATCH']
    schema = UsersEventsRolesSchema
    data_layer = {'session': db.session, 'model': UsersEventsRoles}
