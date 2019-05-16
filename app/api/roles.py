from flask_rest_jsonapi import ResourceDetail, ResourceList

from app.api.bootstrap import api
from app.api.helpers.db import safe_query
from app.api.schema.roles import RoleSchema
from app.models import db
from app.models.role import Role
from app.models.role_invite import RoleInvite
from app.models.users_events_role import UsersEventsRoles
from app.api.helpers.exceptions import UnprocessableEntity
from app.api.helpers.errors import NotFoundError, ServerError
from sqlalchemy.orm.exc import NoResultFound
from flask import Blueprint, request, jsonify
from app.models.users_events_role import UsersEventsRoles as UER
from app.models.role import Role
from app.api.helpers.db import save_to_db

role_misc_routes = Blueprint('role_misc', __name__, url_prefix='/v1')

class RoleList(ResourceList):
    """
    List and create role
    """
    decorators = (api.has_permission('is_admin', methods="POST"),)
    schema = RoleSchema
    data_layer = {'session': db.session,
                  'model': Role}


class RoleDetail(ResourceDetail):
    """
    Role detail by id
    """
    def before_get_object(self, view_kwargs):
        """
        before get method to get the resource id for fetching details
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('role_invite_id') is not None:
                role_invite = safe_query(self, RoleInvite, 'id', view_kwargs['role_invite_id'], 'role_invite_id')
                if role_invite.role_id is not None:
                    view_kwargs['id'] = role_invite.role_id
                else:
                    view_kwargs['id'] = None

        if view_kwargs.get('users_events_role_id') is not None:
                users_events_role = safe_query(self, UsersEventsRoles, 'id', view_kwargs['users_events_role_id'],
                'users_events_role_id')
                if users_events_role.role_id is not None:
                    view_kwargs['id'] = users_events_role.role_id
                else:
                    view_kwargs['id'] = None

    def before_update_object(self, role, data, view_kwargs):
        """
        Method to edit object
        :param role:
        :param data:
        :param view_kwargs:
        :return:
        """
        if data.get('name'):
            if data['name'] in ['organizer', 'coorganizer', 'registrar', 'moderator', 'attendee', 'track_organizer']:
                raise UnprocessableEntity({'data': 'name'}, "The given name cannot be updated")

    def before_delete_object(self, obj, kwargs):
        """
        method to check proper resource name before deleting
        :param obj:
        :param kwargs:
        :return:
        """
        if obj.name in ['organizer', 'coorganizer', 'registrar', 'moderator', 'attendee', 'track_organizer']:
            raise UnprocessableEntity({'data': 'name'}, "The resource with given name cannot be deleted")

    decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
    schema = RoleSchema
    data_layer = {'session': db.session,
                  'model': Role,
                  'methods': {
                      'before_get_object': before_get_object
                  }}


@role_misc_routes.route('/change-organiser', methods=['POST'])
def change_organiser():
    current_organiser_id = request.json.get('current_org_id', None)
    new_organiser_id = request.json.get('new_org_id', None)
    event_id = request.json.get('event_id', None)

    # Check if the user is actually an organiser of the event
    # Delete the User Event Role
    try:
        role_entry_organiser_to_delete = UER.query.filter_by(user_id=current_organiser_id,
                                                            event_id=event_id,
                                                            role_id=1).one()
        db.session.delete(role_entry_organiser_to_delete)

    except NoResultFound:
        return NotFoundError({'source': ''}, 'Organiser Role Entry not found').respond()

    except Exception as e:
        return ServerError({'source': ''}, e).respond()

    # Check if the coorganiser is not found but the earlier entry has been deleted
    # Rollback the last commit in case of exception to restore organiser status
    try:
        role_entry_coorg_to_organiser = UER.query.filter_by(user_id=new_organiser_id,
                                                            event_id=event_id,
                                                            role_id=2).one()
        role_entry_coorg_to_organiser.role_id = 1
        save_to_db(role_entry_coorg_to_organiser)

    except NoResultFound:
        db.session.rollback()
        return NotFoundError({'source': ''}, 'Coorganiser Role Entry not found').respond()

    # Handle Unexpected Errors
    except Exception as e:
        return ServerError({'source': ''}, e).respond()

    return jsonify({
        "message": 'Success'
    })
