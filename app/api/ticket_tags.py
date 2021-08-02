from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.helpers.db import safe_query_kwargs
from app.api.helpers.errors import ForbiddenError
from app.api.helpers.permission_manager import has_access
from app.api.helpers.query import event_query
from app.api.helpers.utilities import require_relationship
from app.api.schema.ticket_tags import TicketTagSchema
from app.models import db
from app.models.ticket import Ticket, TicketTag, ticket_tags_table


class TicketTagListPost(ResourceList):
    """
    List and create TicketTag
    """

    def before_post(self, args, kwargs, data):
        """
        before post method for checking required relationship
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['event'], data)

        if not has_access('is_coorganizer', event_id=data['event']):
            raise ForbiddenError({'source': ''}, 'Co-organizer access is required.')

    schema = TicketTagSchema
    methods = [
        'POST',
    ]
    data_layer = {'session': db.session, 'model': TicketTag}


class TicketTagList(ResourceList):
    """
    List TicketTags based on event_id or ticket_id
    """

    def query(self, view_kwargs):
        """
        method to query Ticket tags based on different params
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(TicketTag)
        if view_kwargs.get('ticket_id'):
            ticket = safe_query_kwargs(Ticket, view_kwargs, 'ticket_id')
            query_ = query_.join(ticket_tags_table).filter_by(ticket_id=ticket.id)
        query_ = event_query(query_, view_kwargs)
        return query_

    view_kwargs = True
    schema = TicketTagSchema
    methods = [
        'GET',
    ]
    data_layer = {'session': db.session, 'model': TicketTag, 'methods': {'query': query}}


class TicketTagDetail(ResourceDetail):
    """
    TicketTag detail by id
    """

    decorators = (
        api.has_permission(
            'is_coorganizer',
            methods="PATCH,DELETE",
            fetch="event_id",
            model=TicketTag,
        ),
    )
    schema = TicketTagSchema
    data_layer = {'session': db.session, 'model': TicketTag}


class TicketTagRelationshipRequired(ResourceRelationship):
    """
    TicketTag Relationship
    """

    decorators = (
        api.has_permission(
            'is_coorganizer',
            methods="PATCH,DELETE",
            fetch="event_id",
            model=TicketTag,
        ),
    )
    schema = TicketTagSchema
    methods = ['GET', 'PATCH']
    schema = TicketTagSchema
    data_layer = {'session': db.session, 'model': TicketTag}


class TicketTagRelationshipOptional(ResourceRelationship):
    """
    TicketTag Relationship
    """

    decorators = (
        api.has_permission(
            'is_coorganizer',
            methods="PATCH,DELETE",
            fetch="event_id",
            model=TicketTag,
        ),
    )
    schema = TicketTagSchema
    schema = TicketTagSchema
    data_layer = {'session': db.session, 'model': TicketTag}
