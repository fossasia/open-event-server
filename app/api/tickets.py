from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields

from app.api.helpers.utilities import dasherize
from app.api.helpers.permissions import jwt_required
from app.models import db
from app.models.ticket import Ticket
from app.models.event import Event


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
    is_fee_absorbed = fields.Boolean()
    min_order = fields.Integer()
    max_order = fields.Integer()
    event = Relationship(attribute='event',
                         self_view='v1.ticket_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'ticket_id': '<id>'},
                         schema='EventSchema',
                         type_='event')


class AllTicketList(ResourceList):

    def query(self, view_kwargs):
        query_ = self.session.query(Ticket)
        if view_kwargs.get('id') is not None:
            query_ = query_.join(Event).filter(Event.id == view_kwargs['id'])
        return query_

    def before_create_object(self, data, view_kwargs):
        if view_kwargs.get('id') is not None:
            event = self.session.query(Event).filter_by(id=view_kwargs['id']).one()
            data['event_id'] = event.id

    decorators = (jwt_required, )
    schema = TicketSchema
    data_layer = {'session': db.session,
                  'model': Ticket,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object
                  }}


class TicketRelationship(ResourceRelationship):
    decorators = (jwt_required, )
    schema = TicketSchema
    data_layer = {'session': db.session,
                  'model': Ticket}


class TicketDetail(ResourceDetail):
    decorators = (jwt_required, )
    schema = TicketSchema
    data_layer = {'session': db.session,
                  'model': Ticket}
