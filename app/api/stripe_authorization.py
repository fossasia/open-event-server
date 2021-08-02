from flask.globals import g
from flask_rest_jsonapi import ResourceDetail, ResourceList
from sqlalchemy.orm.exc import NoResultFound

from app.api.helpers.db import get_count, safe_query_kwargs, save_to_db
from app.api.helpers.errors import ConflictError, ForbiddenError, UnprocessableEntityError
from app.api.helpers.payment import StripePaymentsManager
from app.api.helpers.permission_manager import has_access, is_logged_in
from app.api.helpers.permissions import jwt_required
from app.api.helpers.utilities import require_relationship
from app.api.schema.stripe_authorization import (
    StripeAuthorizationSchema,
    StripeAuthorizationSchemaPublic,
)
from app.models import db
from app.models.event import Event
from app.models.stripe_authorization import StripeAuthorization


class StripeAuthorizationListPost(ResourceList):
    """
    List and Create Stripe Authorization
    """

    def before_post(self, args, kwargs, data):
        """
        before post method to check for required relationship and proper permission
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['event'], data)
        if not has_access('is_organizer', event_id=data['event']):
            raise ForbiddenError({'source': ''}, "Minimum Organizer access required")
        if (
            get_count(
                db.session.query(Event).filter_by(
                    id=int(data['event']), can_pay_by_stripe=False
                )
            )
            > 0
        ):
            raise ForbiddenError(
                {'pointer': ''}, "Stripe payment is disabled for this Event"
            )

    def before_create_object(self, data, view_kwargs):
        """
        method to check if stripe authorization object already exists for an event.
        Raises ConflictError if it already exists.
        If it doesn't, then uses the StripePaymentManager to get the other credentials from Stripe.
        :param data:
        :param view_kwargs:
        :return:
        """
        try:
            self.session.query(StripeAuthorization).filter_by(
                event_id=data['event']
            ).one()
        except NoResultFound:
            credentials = (
                StripePaymentsManager.get_event_organizer_credentials_from_stripe(
                    data['stripe_auth_code']
                )
            )
            if 'error' in credentials:
                raise UnprocessableEntityError(
                    {'pointer': '/data/stripe_auth_code'},
                    credentials['error_description'],
                )
            data['stripe_secret_key'] = credentials['access_token']
            data['stripe_refresh_token'] = credentials['refresh_token']
            data['stripe_publishable_key'] = credentials['stripe_publishable_key']
            data['stripe_user_id'] = credentials['stripe_user_id']
        else:
            raise ConflictError(
                {'pointer': '/data/relationships/event'},
                "Stripe Authorization already exists for this event",
            )

    def after_create_object(self, stripe_authorization, data, view_kwargs):
        """
        after create object method for StripeAuthorizationListPost Class
        :param stripe_authorization: Stripe authorization created from mashmallow_jsonapi
        :param data:
        :param view_kwargs:
        :return:
        """
        event = db.session.query(Event).filter_by(id=int(data['event'])).one()
        event.is_stripe_linked = True
        save_to_db(event)

    schema = StripeAuthorizationSchema
    methods = ['POST']
    data_layer = {
        'session': db.session,
        'model': StripeAuthorization,
        'methods': {
            'before_create_object': before_create_object,
            'after_create_object': after_create_object,
        },
    }


class StripeAuthorizationDetail(ResourceDetail):
    """
    Stripe Authorization Detail Resource by ID
    """

    def before_get(self, args, kwargs):
        """
        method for assigning schema based on access
        :param args:
        :param kwargs:
        :return:
        """
        kwargs = get_id(kwargs)
        if is_logged_in() and has_access('is_coorganizer', event_id=kwargs['id']):
            self.schema = StripeAuthorizationSchema
        else:
            self.schema = StripeAuthorizationSchemaPublic

    def before_get_object(self, view_kwargs):
        """
        method to get id of stripe authorization related to an event
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('event_identifier'):
            event = safe_query_kwargs(
                Event, view_kwargs, 'event_identifier', 'identifier'
            )
            view_kwargs['event_id'] = event.id

        if view_kwargs.get('event_id'):
            stripe_authorization = safe_query_kwargs(
                StripeAuthorization, view_kwargs, 'event_id', 'event_id'
            )
            view_kwargs['id'] = stripe_authorization.id

    def before_delete_object(self, stripe_authorization, view_kwargs):
        if not stripe_authorization:
            return
        g.event = stripe_authorization.event

    def after_delete_object(self, stripe_authorization, view_kwargs):
        """Make work after delete object
        :param stripe_authorization: stripe authorization.
        :param dict view_kwargs: kwargs from the resource view
        """
        if event := g.get('event'):
            event.is_stripe_linked = False
            save_to_db(event)

    decorators = (jwt_required,)
    schema = StripeAuthorizationSchema
    data_layer = {
        'session': db.session,
        'model': StripeAuthorization,
        'methods': {
            'before_get_object': before_get_object,
            'after_delete_object': after_delete_object,
            'before_delete_object': before_delete_object,
        },
    }


class StripeAuthorizationRelationship(ResourceDetail):
    """
    Stripe Authorization Relationship
    """

    decorators = (jwt_required,)
    schema = StripeAuthorizationSchema
    data_layer = {'session': db.session, 'model': StripeAuthorization}


def get_id(view_kwargs):
    """
    method to get the resource id for fetching details
    :param view_kwargs:
    :return:
    """

    if view_kwargs.get('event_identifier') is not None:
        event = safe_query_kwargs(Event, view_kwargs, 'event_identifier', 'identifier')
        if event.id is not None:
            view_kwargs['event_id'] = event.id

    if view_kwargs.get('event_id') is not None:
        stripe_authorization = safe_query_kwargs(
            StripeAuthorization, view_kwargs, 'event_id', 'event_id'
        )
        view_kwargs['id'] = stripe_authorization.id
    return view_kwargs
