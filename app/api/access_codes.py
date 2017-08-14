from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.helpers.db import safe_query
from app.api.helpers.permissions import jwt_required, current_identity
from app.api.helpers.query import event_query
from app.api.helpers.utilities import require_relationship
from app.api.schema.access_codes import AccessCodeSchema
from app.models import db
from app.models.access_code import AccessCode
from app.models.event import Event
from app.models.ticket import Ticket
from app.models.user import User


class AccessCodeList(ResourceList):
    """
    List and create AccessCodes
    """
    def before_post(self, args, kwargs, data):
        require_relationship(['event'], data)

    def query(self, view_kwargs):
        """
        query method for access code list
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(AccessCode)
        query_ = event_query(self, query_, view_kwargs)
        if view_kwargs.get('user_id'):
            user = safe_query(self, User, 'id', view_kwargs['user_id'], 'user_id')
            query_ = query_.join(User).filter(User.id == user.id)
        if view_kwargs.get('ticket_id'):
            ticket = safe_query(self, Ticket, 'id', view_kwargs['ticket_id'], 'ticket_id')
            # access_code - ticket :: many-to-many relationship
            query_ = AccessCode.query.filter(AccessCode.tickets.any(id=ticket.id))
        return query_

    def before_post(self, args, kwargs, data):
        """
        method to add user_id to view_kwargs before post
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        kwargs['user_id'] = current_identity.id

    def before_create_object(self, data, view_kwargs):
        if view_kwargs.get('ticket_id'):
            ticket = safe_query(self, Ticket, 'id', view_kwargs['ticket_id'], 'ticket_id')
            data['event_id'] = ticket.event_id
        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
            data['event_id'] = event.id
        elif view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
            data['event_id'] = event.id
        data['user_id'] = current_identity.id

    def after_create_object(self, obj, data, view_kwargs):
        if view_kwargs.get('ticket_id'):
            ticket = safe_query(self, Ticket, 'id', view_kwargs['ticket_id'], 'ticket_id')
            ticket.access_codes.append(obj)
            self.session.commit()

    view_kwargs = True
    decorators = (jwt_required, )
    schema = AccessCodeSchema
    data_layer = {'session': db.session,
                  'model': AccessCode,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object,
                      'after_create_object': after_create_object
                  }}


class AccessCodeDetail(ResourceDetail):
    """
    AccessCode detail by id
    """
    def before_get_object(self, view_kwargs):
        if view_kwargs.get('ticket_id'):
            ticket = safe_query(self, Ticket, 'id', view_kwargs['ticket_id'], 'ticket_id')
            if ticket.access_code_id:
                view_kwargs['id'] = ticket.access_code_id
            else:
                view_kwargs['id'] = None

    decorators = (jwt_required, )
    schema = AccessCodeSchema
    data_layer = {'session': db.session,
                  'model': AccessCode,
                  'methods': {
                      'before_get_object': before_get_object
                  }}


class AccessCodeRelationshipRequired(ResourceRelationship):
    """
    AccessCode Relationship
    """
    decorators = (jwt_required,)
    methods = ['GET', 'PATCH']
    schema = AccessCodeSchema
    data_layer = {'session': db.session,
                  'model': AccessCode}


class AccessCodeRelationshipOptional(ResourceRelationship):
    """
    AccessCode Relationship
    """
    decorators = (jwt_required,)
    schema = AccessCodeSchema
    data_layer = {'session': db.session,
                  'model': AccessCode}
