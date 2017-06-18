from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields

from app.models import db
from app.models.order import Order
from app.models.ticket_holder import TicketHolder
from app.models.ticket import Ticket
from app.api.helpers.permissions import jwt_required
from app.api.helpers.utilities import dasherize


class AttendeeSchema(Schema):
    """
    Api schema for Attendee Model
    """

    class Meta:
        """
        Meta class for Session Api Schema
        """
        type_ = 'attendee'
        self_view = 'v1.attendee_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    firstname = fields.Str(required=True)
    lastname = fields.Str()
    email = fields.Str()
    address = fields.Str()
    city = fields.Str()
    state = fields.Str()
    country = fields.Str()
    is_checked_in = fields.Boolean()
    pdf_url = fields.Url(required=True)

    ticket = Relationship(attribute='ticket',
                          self_view='v1.attendee_ticket',
                          self_view_kwargs={'id': '<id>'},
                          related_view='v1.ticket_detail',
                          related_view_kwargs={'attendee_id': '<id>'},
                          schema='TicketSchema',
                          type_='ticket')


class AttendeeList(ResourceList):
    """
    List and create Attendees
    """

    def query(self, view_kwargs):
        query_ = self.session.query(TicketHolder)
        if view_kwargs.get('order_id') and view_kwargs.get('ticket_id'):
            query_ = query_.join(Order).filter(Order.id == view_kwargs['order_id'])
            query_ = query_.join(Ticket).filter(Ticket.id == view_kwargs['ticket_id'])
        return query_

    def before_create_object(self, data, view_kwargs):
        if view_kwargs.get('order_id') and view_kwargs.get('ticket_id'):
            data['ticket_id'] = view_kwargs['ticket_id']
            data['order_id'] = view_kwargs['order_id']

    view_kwargs = True
    decorators = (jwt_required,)
    schema = AttendeeSchema
    data_layer = {'session': db.session,
                  'model': TicketHolder,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object}}


class AttendeeDetail(ResourceDetail):
    """
    Attendee detail by id
    """
    decorators = (jwt_required,)
    schema = AttendeeSchema
    data_layer = {'session': db.session,
                  'model': TicketHolder}


class AttendeeRelationship(ResourceRelationship):
    """
    Attendee Relationship
    """
    decorators = (jwt_required,)
    schema = AttendeeSchema
    data_layer = {'session': db.session,
                  'model': TicketHolder}
