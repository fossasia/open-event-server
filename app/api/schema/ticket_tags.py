from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema


class TicketTagSchema(SoftDeletionSchema):
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
    tickets = Relationship(
        self_view='v1.ticket_tag_ticket',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.ticket_list',
        related_view_kwargs={'ticket_tag_id': '<id>'},
        schema='TicketSchemaPublic',
        many=True,
        type_='ticket',
    )
    event = Relationship(
        self_view='v1.ticket_tag_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_detail',
        related_view_kwargs={'ticket_tag_id': '<id>'},
        schema='EventSchemaPublic',
        type_='event',
    )
