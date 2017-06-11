from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from sqlalchemy.orm.exc import NoResultFound
from flask_rest_jsonapi.exceptions import ObjectNotFound


from app.api.helpers.utilities import dasherize
from app.api.helpers.permissions import jwt_required
from app.models import db
from app.models.ticket import Ticket
from app.models.event import Event
from app.models.ticket_holder import TicketHolder
from app.api.helpers.permissions import is_registrar


class TicketSchema(Schema):
    class Meta:
        type_ = 'ticket'
        self_view = 'v1.ticket_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    type = fields.Str(required=True)
    price = fields.Float()
    quantity = fields.Integer()
    description_toggle = fields.Boolean(default=False)
    position = fields.Integer()
    is_fee_absorbed = fields.Boolean()
    sales_starts_at = fields.DateTime()
    sales_ends_at = fields.DateTime()
    is_hidden = fields.Boolean(default=False)
    min_order = fields.Integer()
    max_order = fields.Integer()
    event = Relationship(attribute='event',
                         self_view='v1.ticket_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'ticket_id': '<id>'},
                         schema='EventSchema',
                         type_='event')
    tags = Relationship(attribute='ticket_tag',
                        self_view='v1.ticket_ticket_tag',
                        self_view_kwargs={'id': '<id>'},
                        related_view='v1.ticket_tag_list',
                        related_view_kwargs={'ticket_id': '<id>'},
                        schema='TicketTagSchema',
                        type_='ticket-tag')


class AllTicketList(ResourceList):
    def query(self, view_kwargs):
        query_ = self.session.query(Ticket)
        if view_kwargs.get('id'):
            query_ = query_.join(Event).filter(Event.id == view_kwargs['id'])
        elif view_kwargs.get('identifier'):
            query_ = query_.join(Event).filter(Event.identifier == view_kwargs['identifier'])
        return query_

    def before_create_object(self, data, view_kwargs):
        if view_kwargs.get('id'):
            event = self.session.query(Event).filter_by(id=view_kwargs['id']).one()
            data['event_id'] = event.id
        elif view_kwargs.get('identifier'):
            event = self.session.query(Event).filter_by(identifier=view_kwargs['identifier']).one()
            data['event_id'] = event.id

    decorators = (jwt_required,)
    schema = TicketSchema
    data_layer = {'session': db.session,
                  'model': Ticket,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object
                  }}


class TicketDetail(ResourceDetail):

    def before_get_object(self, view_kwargs):
        if view_kwargs.get('attendee_id') is not None:
            try:
                session = self.session.query(TicketHolder).filter_by(id=view_kwargs['attendee_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'attendee_id'},
                                     "Attendee: {} not found".format(view_kwargs['attendee_id']))
            else:
                if session.ticket_id is not None:
                    view_kwargs['id'] = session.ticket_id
                else:
                    view_kwargs['id'] = None

    decorators = (jwt_required,)
    schema = TicketSchema
    data_layer = {'session': db.session,
                  'model': Ticket}


class TicketRelationship(ResourceRelationship):
    decorators = (jwt_required,)
    schema = TicketSchema
    data_layer = {'session': db.session,
                  'model': Ticket}
