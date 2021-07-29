from marshmallow import validate, validates_schema
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.fields import CustomFormValueField
from app.api.helpers.static import AGE_GROUP_CHOICES
from app.api.helpers.utilities import dasherize
from app.api.helpers.validations import validate_complex_fields_json
from app.api.schema.base import SoftDeletionSchema, TrimmedEmail


class AttendeeSchemaPublic(SoftDeletionSchema):
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

    @validates_schema(pass_original=True)
    def validate_json(self, data, original_data):
        validate_complex_fields_json(self, data, original_data)

    id = fields.Str(dump_only=True)
    firstname = fields.Str(required=True)
    lastname = fields.Str(required=True)
    email = TrimmedEmail(allow_none=True)
    address = fields.Str(allow_none=True)
    city = fields.Str(allow_none=True)
    state = fields.Str(allow_none=True)
    country = fields.Str(allow_none=True)
    job_title = fields.Str(allow_none=True)
    phone = fields.Str(allow_none=True)
    tax_business_info = fields.Str(allow_none=True)
    billing_address = fields.Str(allow_none=True)
    home_address = fields.Str(allow_none=True)
    shipping_address = fields.Str(allow_none=True)
    company = fields.Str(allow_none=True)
    work_address = fields.Str(allow_none=True)
    work_phone = fields.Str(allow_none=True)
    website = fields.Url(allow_none=True)
    blog = fields.Url(allow_none=True)
    twitter = fields.Url(allow_none=True)
    facebook = fields.Url(allow_none=True)
    github = fields.Url(allow_none=True)
    instagram = fields.Url(allow_none=True)
    linkedin = fields.Url(allow_none=True)
    gender = fields.Str(allow_none=True)
    accept_video_recording = fields.Boolean(allow_none=True)
    accept_share_details = fields.Boolean(allow_none=True)
    accept_receive_emails = fields.Boolean(allow_none=True)
    age_group = fields.Str(
        validate=validate.OneOf(choices=AGE_GROUP_CHOICES), allow_none=True
    )
    birth_date = fields.DateTime(allow_none=True)

    ticket_id = fields.Str(allow_none=True)
    is_checked_in = fields.Boolean()
    device_name_checkin = fields.Str(allow_none=True)
    checkin_times = fields.Str(allow_none=True)
    checkout_times = fields.Str(allow_none=True)
    attendee_notes = fields.Str(allow_none=True)
    is_checked_out = fields.Boolean()
    pdf_url = fields.Url(dump_only=True)
    complex_field_values = CustomFormValueField(allow_none=True)
    event = Relationship(
        self_view='v1.attendee_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_detail',
        related_view_kwargs={'attendee_id': '<id>'},
        schema='EventSchema',
        type_='event',
        dump_only=True,
    )
    user = Relationship(
        self_view='v1.attendee_user',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_detail',
        related_view_kwargs={'attendee_id': '<id>'},
        schema='UserSchemaPublic',
        type_='user',
        dump_only=True,
    )
    ticket = Relationship(
        self_view='v1.attendee_ticket',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.ticket_detail',
        related_view_kwargs={'attendee_id': '<id>'},
        schema='TicketSchemaPublic',
        type_='ticket',
        dump_only=True,
    )


class AttendeeSchema(AttendeeSchemaPublic):
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

    order = Relationship(
        self_view='v1.attendee_order',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.order_detail',
        related_view_kwargs={'attendee_id': '<id>'},
        schema='OrderSchema',
        type_='order',
        dump_only=True,
    )
