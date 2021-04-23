from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

from app.api.helpers.utilities import dasherize


class StripeAuthorizationSchemaPublic(Schema):
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
    stripe_publishable_key = fields.Str(dump_only=True)

    event = Relationship(
        self_view='v1.stripe_authorization_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_detail',
        related_view_kwargs={'stripe_authorization_id': '<id>'},
        schema="EventSchema",
        type_='event',
    )


class StripeAuthorizationSchema(StripeAuthorizationSchemaPublic):
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

    stripe_auth_code = fields.Str(load_only=True, required=True)
