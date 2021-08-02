from flask import Blueprint, jsonify, request
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from sqlalchemy.orm.exc import NoResultFound

from app.api.bootstrap import api
from app.api.helpers.db import save_to_db
from app.api.helpers.errors import ConflictError, ForbiddenError, NotFoundError
from app.api.helpers.permission_manager import has_access
from app.api.helpers.query import event_query
from app.api.helpers.role_invite import delete_pending_owner, delete_previous_uer
from app.api.helpers.utilities import require_relationship
from app.api.schema.role_invites import RoleInviteSchema
from app.models import db
from app.models.event import Event
from app.models.role import Role
from app.models.role_invite import RoleInvite
from app.models.user import User
from app.models.users_events_role import UsersEventsRoles

role_invites_misc_routes = Blueprint('role_invites_misc', __name__, url_prefix='/v1')


class RoleInviteListPost(ResourceList):
    """
    Create role invites
    """

    def before_post(self, args, kwargs, data):
        """
        before get method to get the resource id for fetching details
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['event', 'role'], data)
        if not has_access('is_organizer', event_id=data['event']):
            raise ForbiddenError({'source': ''}, 'Organizer access is required.')

    def before_create_object(self, data, view_kwargs):
        """
        before create object method for RoleInviteListPost Class
        :param data:
        :param view_kwargs:
        :return:
        """
        if 'email' in data and 'event' in data:
            role_already_exists = RoleInvite.query.filter_by(
                email=data['email'], event_id=data['event']
            ).count()
        if role_already_exists:
            raise ConflictError(
                {'source': '/data'}, 'Role Invite has already been sent for this email.'
            )
        if data['role_name'] == 'owner' and not has_access(
            'is_owner', event_id=data['event']
        ):
            raise ForbiddenError({'source': ''}, 'Owner access is required.')
        if data['role_name'] == 'owner':
             delete_pending_owner(data['event'])

    def after_create_object(self, role_invite, data, view_kwargs):
        """
        after create object method for role invite links
        :param role_invite:
        :param data:
        :param view_kwargs:
        :return:
        """
        role_invite.send_invite()

    view_kwargs = True
    methods = ['POST']
    schema = RoleInviteSchema
    data_layer = {
        'session': db.session,
        'model': RoleInvite,
        'methods': {
            'before_create_object': before_create_object,
            'after_create_object': after_create_object,
        },
    }


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
        query_ = event_query(query_, view_kwargs)
        return query_

    view_kwargs = True
    methods = ['GET']
    decorators = (api.has_permission('is_coorganizer', fetch='event_id'),)
    schema = RoleInviteSchema
    data_layer = {'session': db.session, 'model': RoleInvite, 'methods': {'query': query}}


class RoleInviteDetail(ResourceDetail):
    """
    Role invite detail by id
    """

    def before_delete_object(self, role_invite, view_kwargs):
        """
        method to check for proper permissions for deleting
        :param order:
        :param view_kwargs:
        :return:
        """
        if role_invite.status == 'accepted':
            raise ConflictError(
                {'pointer': '/data/status'}, 'You cannot delete an accepted role invite.'
            )

    methods = ['GET', 'DELETE']
    decorators = (
        api.has_permission(
            'is_organizer',
            methods="DELETE",
            fetch="event_id",
            model=RoleInvite,
        ),
    )
    schema = RoleInviteSchema
    data_layer = {
        'session': db.session,
        'model': RoleInvite,
        'methods': {'before_delete_object': before_delete_object},
    }


class RoleInviteRelationship(ResourceRelationship):
    """
    Role invite Relationship
    """

    methods = ['GET', 'PATCH']
    schema = RoleInviteSchema
    data_layer = {'session': db.session, 'model': RoleInvite}


@role_invites_misc_routes.route('/role_invites/accept-invite', methods=['POST'])
def accept_invite():
    token = request.json['data']['token']
    try:
        role_invite = RoleInvite.query.filter_by(hash=token).one()
    except NoResultFound:
        raise NotFoundError({'source': ''}, 'Role Invite Not Found')
    else:
        try:
            user = User.query.filter_by(email=role_invite.email).first()
        except NoResultFound:
            raise NotFoundError(
                {'source': ''}, 'User corresponding to role invite not Found'
            )
        try:
            role = Role.query.filter_by(name=role_invite.role_name).first()
        except NoResultFound:
            raise NotFoundError(
                {'source': ''}, 'Role corresponding to role invite not Found'
            )
        event = Event.query.filter_by(id=role_invite.event_id).first()
        uer = (
            UsersEventsRoles.query.filter_by(user=user)
            .filter_by(event=event)
            .filter_by(role=role)
            .first()
        )

        if not uer:
            if role_invite.role_name == 'owner':
                past_owner = UsersEventsRoles.query.filter_by(
                    event=event, role=role
                ).first()
                oldrole = Role.query.filter_by(name='organizer').first()
                prevuser = User.query.filter_by(id=past_owner.user_id).first()
                if past_owner:
                    delete_previous_uer(past_owner)
                    puer = UsersEventsRoles(user=prevuser, event=event, role=oldrole)
                    save_to_db(puer, 'User Event Role changed')
            role_invite.status = "accepted"
            save_to_db(role_invite, 'Role Invite Accepted')
            # reset the group of event
            event.group_id = None
            save_to_db(event, 'Group ID Removed')
            uer = UsersEventsRoles(user=user, event=event, role=role)
            save_to_db(uer, 'User Event Role Created')
            if not user.is_verified:
                user.is_verified = True
                save_to_db(user, 'User verified')

    return jsonify(
        {
            "email": user.email,
            "event": role_invite.event_id,
            "event_identifier": role_invite.event.identifier,
            "name": user.fullname if user.fullname else None,
            "role": uer.role.name,
        }
    )


@role_invites_misc_routes.route('/role_invites/user', methods=['POST'])
def fetch_user():
    token = request.json['data']['token']
    try:
        role_invite = RoleInvite.query.filter_by(hash=token).one()
    except NoResultFound:
        raise NotFoundError({'source': ''}, 'Role Invite Not Found')
    else:
        return jsonify({"email": role_invite.email})
