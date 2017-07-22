from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from sqlalchemy.orm.exc import NoResultFound
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.helpers.utilities import dasherize
from app.api.helpers.permissions import jwt_required
from app.models import db
from app.models.ticket import Ticket, TicketTag, ticket_tags_table
from app.models.event import Event
from app.api.helpers.db import safe_query
from app.api.helpers.utilities import require_relationship
from app.api.helpers.exceptions import ForbiddenException
from app.api.helpers.permission_manager import has_access


class TicketTagSchema(Schema):
    """
    Api schema for TicketTag Model
    """

    class Meta:
        """
        Meta class for TicketTag Api Schema
        """
        type_ = 'ticket-tag'
        self_view = 'v1.ticket_tag_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(allow_none=True)
    tickets = Relationship(attribute='tickets',
                           self_view='v1.ticket_tag_ticket',
                           self_view_kwargs={'id': '<id>'},
                           related_view='v1.ticket_list',
                           related_view_kwargs={'ticket_tag_id': '<id>'},
                           schema='TicketSchema',
                           many=True,
                           type_='ticket')
    event = Relationship(attribute='event',
                         self_view='v1.ticket_tag_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'ticket_tag_id': '<id>'},
                         schema='EventSchema',
                         type_='event')


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
            raise ForbiddenException({'source': ''}, 'Co-organizer access is required.')

    def after_create_object(self, obj, data, view_kwargs):
        """
        method to add ticket tags and ticket in association table
        :param obj:
        :param data:
        :param view_kwargs:
        :return:
        """
        if 'tickets' in data:
            ticket_ids = data['tickets']
            for ticket_id in ticket_ids:
                try:
                    ticket = Ticket.query.filter_by(id=ticket_id).one()
                except NoResultFound:
                    raise ObjectNotFound({'parameter': 'ticket_id'},
                                         "Ticket: {} not found".format(ticket_id))
                else:
                    ticket.tags.append(obj)
                    self.session.commit()

    schema = TicketTagSchema
    data_layer = {'session': db.session,
                  'model': TicketTag,
                  'methods': {
                    'after_create_object': after_create_object
                  }}


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
            ticket = safe_query(self, Ticket, 'id', view_kwargs['ticket_id'], 'ticket_id')
            query_ = query_.join(ticket_tags_table).filter_by(ticket_id=ticket.id)
        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
            query_ = query_.join(Event).filter(Event.id == event.id)
        elif view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
            query_ = query_.join(Event).filter(Event.id == event.id)
        return query_

    view_kwargs = True
    schema = TicketTagSchema
    methods = ['GET', ]
    data_layer = {'session': db.session,
                  'model': TicketTag,
                  'methods': {
                      'query': query
                  }}


class TicketTagDetail(ResourceDetail):
    """
    TicketTag detail by id
    """
    decorators = (jwt_required,)
    schema = TicketTagSchema
    data_layer = {'session': db.session,
                  'model': TicketTag}


class TicketTagRelationshipRequired(ResourceRelationship):
    """
    TicketTag Relationship
    """
    decorators = (jwt_required,)
    methods = ['GET', 'PATCH']
    schema = TicketTagSchema
    data_layer = {'session': db.session,
                  'model': TicketTag}


class TicketTagRelationshipOptional(ResourceRelationship):
    """
    TicketTag Relationship
    """
    decorators = (jwt_required,)
    schema = TicketTagSchema
    data_layer = {'session': db.session,
                  'model': TicketTag}
