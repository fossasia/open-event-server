from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.helpers.db import save_to_db
from app.api.helpers.exceptions import ForbiddenException
from app.api.helpers.exceptions import UnprocessableEntity
from app.api.helpers.mail import send_email_role_invite
from app.api.helpers.notification import send_notif_event_role
from app.api.helpers.permission_manager import has_access
from app.api.helpers.query import event_query
from app.api.helpers.utilities import require_relationship
from app.api.schema.role_invites import RoleInviteSchema
from app.models import db
from app.models.event import Event
from app.models.role import Role
from app.models.role_invite import RoleInvite
from app.models.user import User
from app.models.users_events_role import UsersEventsRoles
from app.settings import get_settings
from flask import jsonify, request, Blueprint
from app.api.helpers.errors import NotFoundError
from sqlalchemy.orm.exc import NoResultFound


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
            raise ForbiddenException({'source': ''}, 'Organizer access is required.')

    def after_create_object(self, role_invite, data, view_kwargs):
        """
        after create object method for role invite links
        :param role_invite:
        :param data:
        :param view_kwargs:
        :return:
        """
        user = User.query.filter_by(email=role_invite.email).first()
        event = Event.query.filter_by(id=role_invite.event_id).first()
        frontend_url = get_settings()['frontend_url']
        link = "{}/e/{}/role-invites?token={}" \
            .format(frontend_url, event.identifier, role_invite.hash)

        send_email_role_invite(role_invite.email, role_invite.role_name, event.name, link)
        if user:
            send_notif_event_role(user, role_invite.role_name, event.name, link, event.id)

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
    decorators = (api.has_permission('is_coorganizer', fetch='event_id', fetch_as="event_id"),)
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
            if not has_access('is_user_itself', user_id=user.id):
                raise UnprocessableEntity({'source': ''}, "Only users can edit their own status")
        if not user and not has_access('is_organizer', event_id=role_invite.event_id):
            raise UnprocessableEntity({'source': ''}, "User not registered")
        if not has_access('is_organizer', event_id=role_invite.event_id) and (len(list(data.keys())) > 1 or
                                                                              'status' not in data):
            raise UnprocessableEntity({'source': ''}, "You can only change your status")

    decorators = (api.has_permission('is_organizer', methods="DELETE", fetch="event_id", fetch_as="event_id",
                                     model=RoleInvite),)
    schema = RoleInviteSchema
    data_layer = {'session': db.session,
                  'model': RoleInvite,
                  'methods': {'before_update_object': before_update_object}}


class RoleInviteRelationship(ResourceRelationship):
    """
    Role invite Relationship
    """
    methods = ['GET', 'PATCH']
    schema = RoleInviteSchema
    data_layer = {'session': db.session,
                  'model': RoleInvite}


@role_invites_misc_routes.route('/role_invites/accept-invite', methods=['POST'])
def accept_invite():
    token = request.json['data']['token']
    try:
        role_invite = RoleInvite.query.filter_by(hash=token).one()
    except NoResultFound:
        return NotFoundError({'source': ''}, 'Role Invite Not Found').respond()
    else:
        try:
            user = User.query.filter_by(email=role_invite.email).first()
        except NoResultFound:
            return NotFoundError({'source': ''}, 'User corresponding to role invite not Found').respond()
        try:
            role = Role.query.filter_by(name=role_invite.role_name).first()
        except NoResultFound:
            return NotFoundError({'source': ''}, 'Role corresponding to role invite not Found').respond()
        event = Event.query.filter_by(id=role_invite.event_id).first()
        uer = UsersEventsRoles.query.filter_by(user=user).filter_by(
            event=event).filter_by(role=role).first()
        if not uer:
            role_invite.status = "accepted"
            save_to_db(role_invite, 'Role Invite Accepted')
            uer = UsersEventsRoles(user, event, role)
            save_to_db(uer, 'User Event Role Created')
            if not user.is_verified:
                user.is_verified = True
                save_to_db(user, 'User verified')

    return jsonify({
        "email": user.email,
        "event": role_invite.event_id,
        "name": user.fullname if user.fullname else None
    })


@role_invites_misc_routes.route('/role_invites/user', methods=['POST'])
def fetch_user():
    token = request.json['data']['token']
    try:
        role_invite = RoleInvite.query.filter_by(hash=token).one()
    except NoResultFound:
        return NotFoundError({'source': ''}, 'Role Invite Not Found').respond()
    else:
        return jsonify({
            "email": role_invite.email
        })
