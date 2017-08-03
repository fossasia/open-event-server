from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
import marshmallow.validate as validate
from marshmallow import validates_schema

from app.api.helpers.utilities import dasherize
from app.models import db
from app.settings import get_settings
from app.models.event import Event
from app.models.role_invite import RoleInvite
from app.models.users_events_role import UsersEventsRoles
from app.models.role import Role
from app.models.user import User
from app.api.bootstrap import api
from app.api.helpers.db import save_to_db
from app.api.helpers.utilities import require_relationship
from app.api.helpers.permission_manager import has_access
from app.api.helpers.exceptions import UnprocessableEntity
from app.api.helpers.exceptions import ForbiddenException
from app.api.helpers.query import event_query
from app.api.helpers.mail import send_email_role_invite


class RoleInviteSchema(Schema):
    """
    Api Schema for role invite model
    """

    class Meta:
        """
        Meta class for role invite Api Schema
        """
        type_ = 'role-invite'
        self_view = 'v1.role_invite_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    @validates_schema(pass_original=True)
    def validate_satus(self, data, original_data):
        if 'role' in data and 'role_name' in data:
            role = Role.query.filter_by(id=data['role']).one()
            if role.name != data['role_name']:
                raise UnprocessableEntity({'pointer': '/data/attributes/role'},
                                          "Role id do not match role name")
        if 'id' in original_data['data']:
            role_invite = RoleInvite.query.filter_by(id=original_data['data']['id']).one()
            if 'role' not in data:
                data['role'] = role_invite.role.id
            if 'role_name' in data:
                role = Role.query.filter_by(id=data['role']).one()
                if role.name != data['role_name']:
                    raise UnprocessableEntity({'pointer': '/data/attributes/role'},
                                              "Role id do not match role name")


    id = fields.Str(dump_only=True)
    email = fields.Str(required=True)
    hash = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True, timezone=True)
    role_name = fields.Str(validate=validate.OneOf(choices=["organizer", "coorganizer", "track_organizer",
                           "moderator", "attendee", "registrar"]))
    status = fields.Str(validate=validate.OneOf(choices=["pending", "accepted", "declined"]),
                        default="pending")
    event = Relationship(attribute='event',
                         self_view='v1.role_invite_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'role_invite_id': '<id>'},
                         schema='EventSchema',
                         type_='event')
    role = Relationship(attribute='role',
                        self_view='v1.role_invite_role',
                        self_view_kwargs={'id': '<id>'},
                        related_view='v1.role_detail',
                        related_view_kwargs={'role_invite_id': '<id>'},
                        schema='RoleSchema',
                        type_='role')


class RoleInviteListPost(ResourceList):
    """
    Create role invites
    """

    def before_post(self, args, kwargs, data):
        require_relationship(['event', 'role'], data)
        if not has_access('is_organizer', event_id=data['event']):
            raise ForbiddenException({'source': ''}, 'Organizer access is required.')

    def after_create_object(self, role_invite, data, view_kwargs):
        user = User.query.filter_by(email=role_invite.email).first()
        if 'status' in data and data['status'] == 'accepted':
            role = Role.query.filter_by(name=role_invite.role_name).first()
            event = Event.query.filter_by(id=role_invite.event_id).first()
            uer = UsersEventsRoles.query.filter_by(user=user).filter_by(event=event).filter_by(role=role).first()
            if not uer:
                uer = UsersEventsRoles(user, event, role)
                save_to_db(uer, 'Role Invite accepted')

        event = Event.query.filter_by(id=role_invite.event_id).first()
        frontend_url = get_settings()['frontend_url']
        link = "{}/events/{}/role-invites/{}" \
            .format(frontend_url, event.id, role_invite.hash)
        send_email_role_invite(role_invite.email, role_invite.role_name, event.name, link)


    view_kwargs = True
    methods = ['POST']
    schema = RoleInviteSchema
    data_layer = {'session': db.session,
                  'model': RoleInvite,
                  'methods': {
                      'after_create_object': after_create_object
                  }}


class RoleInviteList(ResourceList):
    """
    List role invites based on event_id
    """
    def query(self, view_kwargs):
        """
        query method for role invites list
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(RoleInvite)
        query_ = event_query(self, query_, view_kwargs)
        return query_

    view_kwargs = True
    methods = ['GET']
    decorators = (api.has_permission('is_organizer', fetch='event_id', fetch_as="event_id"),)
    schema = RoleInviteSchema
    data_layer = {'session': db.session,
                  'model': RoleInvite,
                  'methods': {
                      'query': query
                  }}


class RoleInviteDetail(ResourceDetail):
    """
    Role invite detail by id
    """
    def before_update_object(self, role_invite, data, view_kwargs):
        """
        Method to edit object
        :param role_invite:
        :param data:
        :param view_kwargs:
        :return:
        """
        user = User.query.filter_by(email=role_invite.email).first()
        if user:
            if not has_access('is_user_itself', id=user.id):
                raise UnprocessableEntity({'source': ''}, "Only users can edit their own status")
        if not user and not has_access('is_organizer', event_id=role_invite.event_id):
            raise UnprocessableEntity({'source': ''}, "User not registered")
        if not has_access('is_organizer', event_id=role_invite.event_id) and (len(data.keys())>1 or 'status' not in data):
            raise UnprocessableEntity({'source': ''}, "You can only change your status")

    def after_update_object(self, role_invite, data, view_kwargs):
        user = User.query.filter_by(email=role_invite.email).first()
        if 'status' in data and data['status'] == 'accepted':
            role = Role.query.filter_by(name=role_invite.role_name).first()
            event = Event.query.filter_by(id=role_invite.event_id).first()
            uer = UsersEventsRoles.query.filter_by(user=user).filter_by(event=event).filter_by(role=role).first()
            if not uer:
                uer = UsersEventsRoles(user, event, role)
                save_to_db(uer, 'Role Invite accepted')
    decorators = (api.has_permission('is_organizer', methods="DELETE", fetch="event_id", fetch_as="event_id",
                                     model=RoleInvite),)
    schema = RoleInviteSchema
    data_layer = {'session': db.session,
                  'model': RoleInvite,
                  'methods': {'before_update_object': before_update_object,
                              'after_update_object': after_update_object}}


class RoleInviteRelationship(ResourceRelationship):
    """
    Role invite Relationship
    """
    methods = ['GET', 'PATCH']
    schema = RoleInviteSchema
    data_layer = {'session': db.session,
                  'model': RoleInvite}
