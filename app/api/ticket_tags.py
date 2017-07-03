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
    name = fields.Str()
    tickets = Relationship(attribute='tickets',
                          self_view='v1.ticket_tag_ticket',
                          self_view_kwargs={'id': '<id>'},
                          related_view='v1.ticket_list',
                          related_view_kwargs={'ticket_tag_id': '<id>'},
                          schema='TicketSchema',
                          type_='ticket')
    event = Relationship(attribute='event',
                         self_view='v1.ticket_tag_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'ticket_tag_id': '<id>'},
                         schema='EventSchema',
                         type_='event')


class TicketTagList(ResourceList):
    """
    List and create TicketTag
    """

    def query(self, view_kwargs):
        query_ = self.session.query(TicketTag)
        if view_kwargs.get('ticket_id'):
            ticket = self.session.query(Ticket).filter_by(id=view_kwargs['ticket_id']).one()
            query_ = query_.join(ticket_tags_table).filter_by(ticket_id=ticket.id)
        if view_kwargs.get('event_id'):
            query_ = query_.join(Event).filter(Event.id == view_kwargs['event_id'])
        elif view_kwargs.get('identifier'):
            query_ = query_.join(Event).filter(Event.identifier == view_kwargs['identifier'])
        return query_

    def before_create_object(self, data, view_kwargs):
        if view_kwargs.get('ticket_id'):
            ticket = self.session.query(Ticket).filter_by(id=view_kwargs['ticket_id']).one()
            data['event_id'] = ticket.event_id
        elif view_kwargs.get('event_id'):
            event = self.session.query(Event).filter_by(id=view_kwargs['event_id']).one()
            data['event_id']=event.id
        elif view_kwargs.get('event_identifier'):
            event = self.session.query(Event).filter_by(id=view_kwargs['event_identifier']).one()
            data['event_id']=event.id

    def after_create_object(self, obj, data, view_kwargs):
        if view_kwargs.get('ticket_id'):
            ticket = self.session.query(Ticket).filter_by(id=view_kwargs['ticket_id']).one()
            ticket.tags.append(obj)
            self.session.commit()

    view_kwargs = True
    decorators = (jwt_required,)
    schema = TicketTagSchema
    data_layer = {'session': db.session,
                  'model': TicketTag,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object,
                      'after_create_object': after_create_object
                  }}


class TicketTagDetail(ResourceDetail):
    """
    TicketTag detail by id
    """
    decorators = (jwt_required, )
    schema = TicketTagSchema
    data_layer = {'session': db.session,
                  'model': TicketTag}

class TicketTagRelationship(ResourceRelationship):
    """
    TicketTag Relationship
    """
    decorators = (jwt_required,)
    schema = TicketTagSchema
    data_layer = {'session': db.session,
                  'model': TicketTag}
