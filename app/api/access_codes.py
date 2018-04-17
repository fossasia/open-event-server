from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound
from app.api.helpers.exceptions import ForbiddenException

from app.api.bootstrap import api
from app.api.helpers.db import safe_query
from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required
from app.api.helpers.query import event_query
from app.api.helpers.utilities import require_relationship
from app.api.schema.access_codes import AccessCodeSchema
from app.models import db
from app.models.access_code import AccessCode
from app.models.ticket import Ticket
from app.models.user import User


class AccessCodeListPost(ResourceList):
    """
    Create AccessCodes
    """
    def before_post(self, args, kwargs, data):
        """
        before post method to check for required relationships and permissions
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['event', 'user'], data)
        if not has_access('is_coorganizer', event_id=data['event']):
            raise ObjectNotFound({'parameter': 'event_id'},
                                 "Event: {} not found".format(data['event']))

    schema = AccessCodeSchema
    methods = ['POST', ]
    data_layer = {'session': db.session,
                  'model': AccessCode
                  }


class AccessCodeList(ResourceList):
    """
    List AccessCodes
    """
    def query(self, view_kwargs):
        """
        Method to get access codes list based on different view_kwargs
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(AccessCode)
        query_ = event_query(self, query_, view_kwargs, permission='is_coorganizer')
        if view_kwargs.get('user_id'):
            user = safe_query(self, User, 'id', view_kwargs['user_id'], 'user_id')
            if not has_access('is_user_itself', user_id=user.id):
                raise ForbiddenException({'source': ''}, 'Access Forbidden')
            query_ = query_.join(User).filter(User.id == user.id)
        if view_kwargs.get('ticket_id'):
            ticket = safe_query(self, Ticket, 'id', view_kwargs['ticket_id'], 'ticket_id')
            if not has_access('is_coorganizer', event_id=ticket.event_id):
                raise ForbiddenException({'source': ''}, 'Access Forbidden')
            # access_code - ticket :: many-to-many relationship
            query_ = AccessCode.query.filter(AccessCode.tickets.any(id=ticket.id))
            query_
        return query_

    view_kwargs = True
    methods = ['GET', ]
    schema = AccessCodeSchema
    data_layer = {'session': db.session,
                  'model': AccessCode,
                  'methods': {
                      'query': query,
                  }}


class AccessCodeDetail(ResourceDetail):
    """
    AccessCode detail by id
    """

    decorators = (api.has_permission('is_coorganizer', fetch='event_id',
                  fetch_as="event_id", model=AccessCode, methods="GET, PATCH"),
                  api.has_permission('is_coorganizer_but_not_admin', fetch='event_id',
                  fetch_as="event_id", model=AccessCode, methods="DELETE"),)
    schema = AccessCodeSchema
    data_layer = {'session': db.session,
                  'model': AccessCode
                  }


class AccessCodeRelationshipRequired(ResourceRelationship):
    """
    AccessCode Relationship Required
    """
    decorators = (jwt_required,)
    methods = ['GET', 'PATCH']
    schema = AccessCodeSchema
    data_layer = {'session': db.session,
                  'model': AccessCode}


class AccessCodeRelationshipOptional(ResourceRelationship):
    """
    AccessCode Relationship Optional
    """
    decorators = (jwt_required,)
    schema = AccessCodeSchema
    data_layer = {'session': db.session,
                  'model': AccessCode}
