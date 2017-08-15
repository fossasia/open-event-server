from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema, Relationship

from app.api.helpers.utilities import dasherize


class AttendeeSchema(Schema):
    """
    Api schema for Ticket Holder Model
    """

    class Meta:
        """
        Meta class for Attendee API Schema
        """
        type_ = 'attendee'
        self_view = 'v1.attendee_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    firstname = fields.Str(required=True)
    lastname = fields.Str(allow_none=True)
    email = fields.Str(allow_none=True)
    address = fields.Str(allow_none=True)
    city = fields.Str(allow_none=True)
    state = fields.Str(allow_none=True)
    country = fields.Str(allow_none=True)
    ticket_id = fields.Str(allow_none=True)
    is_checked_in = fields.Boolean()
    pdf_url = fields.Url(required=True)
    ticket = Relationship(attribute='ticket',
                          self_view='v1.attendee_ticket',
                          self_view_kwargs={'id': '<id>'},
                          related_view='v1.ticket_detail',
                          related_view_kwargs={'attendee_id': '<id>'},
                          schema='TicketSchema',
                          type_='ticket')
    event = Relationship(attribute='event',
                         self_view='v1.attendee_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'attendee_id': '<id>'},
                         schema='EventSchemaPublic',
                         type_='event')

    order = Relationship(self_view='v1.attendee_order',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.order_detail',
                         related_view_kwargs={'attendee_id': '<id>'},
                         schema='OrderSchema',
                         type_='order')
