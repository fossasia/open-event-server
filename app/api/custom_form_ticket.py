from flask_jwt_extended import current_user, verify_jwt_in_request
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.bootstrap import api
from app.api.helpers.db import safe_query, safe_query_kwargs
from app.api.helpers.permission_manager import has_access, is_logged_in
from app.api.helpers.permissions import jwt_required
from app.api.helpers.query import event_query
from app.api.helpers.utilities import require_relationship
from app.api.schema.custom_form_ticket import CustomFormTicketSchema
from app.models import db
from app.models.custom_form_ticket import CustomFormTickets 
from app.models.event import Event


class CustomFormTicketListPost(ResourceList):
    """
    Create and List Custom Forms
    """

    def before_post(self, args, kwargs, data):
        """
        method to check for required relationship with event
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['ticket'], data)
        require_relationship(['event'], data)
        if not has_access('is_coorganizer', ticket=data['ticket']):
            raise ObjectNotFound(
                {'parameter': 'ticket_id'}, "ticket: {} not found".format(data['ticket_id'])
            )
        if not has_access('is_coorganizer', event=data['event']):
            raise ObjectNotFound(
                {'parameter': 'event_id'}, "event: {} not found".format(data['event_id'])
            )

    schema = CustomFormTicketSchema
    methods = [
        'POST',
    ]
    data_layer = {'session': db.session, 'model': CustomFormTickets}

class CustomFormTicketDetail(ResourceDetail):
    """
    CustomFormTicket Resource
    """

    schema = CustomFormTicketSchema
    data_layer = {'session': db.session, 'model': CustomFormTickets}

class CustomFormTicketRelationshipRequire(ResourceRelationship):
    """
    CustomFormTicket Relationship (Required)
    """

    decorators = (jwt_required,)
    methods = ['GET', 'PATCH']
    schema = CustomFormTicketSchema
    data_layer = {'session': db.session, 'model': CustomFormTickets}

class CustomFormTicketList(ResourceList):
    """
    List CustomFormTickets based on different params
    """

    def query(self, view_kwargs):
        """
        query method for resource list
        :param view_kwargs:
        :return:
        """

        if view_kwargs.get('event_id'):
            events = safe_query_kwargs(Event, view_kwargs, 'event_id')
            query_ = self.session.query(CustomFormTickets).filter_by(event_id=events.id)
            if view_kwargs.get('form_id'):
                query_ = query_.filter_by(form_id=CustomFormTickets.form_id)
        query_ = event_query(query_, view_kwargs)

        return query_

    view_kwargs = True
    methods = [
        'GET',
    ]
    schema = CustomFormTicketSchema
    data_layer = {
        'session': db.session,
        'model': CustomFormTickets,
        'methods': {
            'query': query,
        },
    }