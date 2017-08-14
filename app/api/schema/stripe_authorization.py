from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema, Relationship

from app.api.helpers.utilities import dasherize


class StripeAuthorizationSchema(Schema):
    """
        Stripe Authorization Schema
    """

    class Meta:
        """
        Meta class for StripeAuthorization Api Schema
        """
        type_ = 'stripe-authorization'
        self_view = 'v1.stripe_authorization_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    stripe_secret_key = fields.Str(required=True)
    stripe_refresh_token = fields.Str(required=True)
    stripe_publishable_key = fields.Str(required=True)
    stripe_user_id = fields.Str(required=True)
    stripe_email = fields.Str(required=True)

    event = Relationship(self_view='v1.stripe_authorization_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'id': '<id>'},
                         schema="EventSchema",
                         type_='event')
