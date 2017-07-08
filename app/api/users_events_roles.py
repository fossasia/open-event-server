from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.helpers.utilities import dasherize
from app.models import db
from app.api.helpers.db import save_to_db
from app.models.event import Event
from app.models.user import User
from app.models.users_events_role import UsersEventsRoles
from app.models.role_invite import RoleInvite
from app.api.helpers.permissions import jwt_required
from app.api.helpers.db import safe_query


class UsersEventsRolesSchema(Schema):
    """
    Api Schema for user-events-role model
    """

    class Meta:
        """
        Meta class for user-events-role Api Schema
        """
        type_ = 'users-events-role'
        self_view = 'v1.users_events_role_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    event = Relationship(attribute='event',
                         self_view='v1.users_events_role_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'users_events_role_id': '<id>'},
                         schema='EventSchema',
                         type_='event')
    role = Relationship(attribute='role',
                        self_view='v1.users_events_role_role',
                        self_view_kwargs={'id': '<id>'},
                        related_view='v1.role_detail',
                        related_view_kwargs={'users_events_role_id': '<id>'},
                        schema='RoleSchema',
                        type_='role')
    user = Relationship(attribute='user',
                        self_view='v1.users_events_role_user',
                        self_view_kwargs={'id': '<id>'},
                        related_view='v1.user_detail',
                        related_view_kwargs={'users_events_role_id': '<id>'},
                        schema='UserSchema',
                        type_='user')


class UsersEventsRolesList(ResourceList):
    """
    List and create user-events-roles
    """

    def query(self, view_kwargs):
        """
        query method for role invites list
        :param view_kwargs:
        :return:
        """

        query_ = self.session.query(RoleInvite)
        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
            query_ = query_.filter_by(event_id=event.id)
        elif view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
            query_ = query_.join(Event).filter(Event.id == event.id)
        return query_

    def before_create_object(self, data, view_kwargs):
        """
        method to create object before post
        :param data:
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
            data['event_id'] = event.id

        elif view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
            data['event_id'] = event.id
        email = safe_query(self, User, 'id', data['user'], 'user_id').email
        invite = self.session.query(RoleInvite).filter_by(email=email).filter_by(role_id=data['role'])\
                .filter_by(event_id=data['event_id']).one_or_none()
        if not invite:
            raise ObjectNotFound({'parameter': 'invite'}, "Object: not found")

    def after_create_object(self, obj, data, view_kwargs):
        """
        method to create object after post
        :param data:
        :param view_kwargs:
        :return:
        """
        email = safe_query(self, User, 'id', data['user'], 'user_id').email
        invite = self.session.query(RoleInvite).filter_by(email=email).filter_by(role_id=data['role'])\
                .filter_by(event_id=data['event_id']).one_or_none()
        if invite:
            invite.status = "accepted"
            save_to_db(invite)
        else:
            raise ObjectNotFound({'parameter': 'invite'}, "Object: not found")

    view_kwargs = True
    decorators = (jwt_required,)
    schema = UsersEventsRolesSchema
    data_layer = {'session': db.session,
                  'model': UsersEventsRoles,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object,
                      'after_create_object': after_create_object
                  }}


class UsersEventsRolesDetail(ResourceDetail):
    """
    User-events-role detail by id
    """

    decorators = (jwt_required,)
    schema = UsersEventsRolesSchema
    data_layer = {'session': db.session,
                  'model': UsersEventsRoles}


class UsersEventsRolesRelationship(ResourceRelationship):
    """
    User-events-role Relationship
    """
    decorators = (jwt_required,)
    schema = UsersEventsRolesSchema
    data_layer = {'session': db.session,
                  'model': UsersEventsRoles}
