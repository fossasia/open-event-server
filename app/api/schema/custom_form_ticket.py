from marshmallow import validate
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

from app.api.helpers.utilities import dasherize
from utils.common import use_defaults


@use_defaults()
class CustomFormTicketSchema(Schema):
    """
    API Schema for Custom Form Ticket database model
    """

    class Meta:
        """
        Meta class for CustomFormTicket Schema
        """

        type_ = 'custom-form-ticket'
        self_view = 'v1.custom_form_ticket_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Integer(dump_only=True)
    form_id = fields.Str(required=True)
    ticket = Relationship(
        self_view='v1.custom_form_ticket_ticket',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.ticket_detail',
        related_view_kwargs={'custom_form_ticket_id': '<id>'},
        schema='TicketSchemaPublic',
        type_='ticket',
    )
    event = Relationship(
        self_view='v1.custom_form_ticket_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_detail',
        related_view_kwargs={'custom_form_ticket_id': '<id>'},
        schema='EventSchemaPublic',
        type_='event',
    )
