from flask_rest_jsonapi import ResourceDetail, ResourceList
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from sqlalchemy.orm.exc import NoResultFound

from app.api.bootstrap import api
from app.api.helpers.db import safe_query
from app.api.helpers.exceptions import ForbiddenException, ConflictException
from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required
from app.models import db
from app.models.event import Event
from app.api.helpers.utilities import dasherize, require_relationship
from app.models.stripe_authorization import StripeAuthorization


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


class StripeAuthorizationListPost(ResourceList):
    """
        List and Create Stripe Authorization
    """
    def before_post(self, args, kwargs, data):
        require_relationship(['event'], data)
        if not has_access('is_organizer', event_id=data['event']):
            raise ForbiddenException({'source': ''}, "Minimum Organizer access required")

    def before_create_object(self, data, view_kwargs):
        try:
            self.session.query(StripeAuthorization).filter_by(event_id=data['event']).one()
        except NoResultFound:
            pass
        else:
            raise ConflictException({'pointer': '/data/relationships/event'},
                                    "Stripe Authorization already exists for this event")

    def before_get(self, args, kwargs):
        if not has_access('is_super_admin'):
            raise ForbiddenException({'source': ''}, "Super Admin Access Required")

    schema = StripeAuthorizationSchema
    decorators = (jwt_required, )
    data_layer = {'session': db.session,
                  'model': StripeAuthorization}


class StripeAuthorizationList(ResourceList):
    """
    Stripe Authorization List Resource
    """

    def query(self, view_kwargs):
        query_ = self.session.query(StripeAuthorization)
        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
            query_ = query_.filter_by(event_id=event.id)

        if view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['identifier'], 'event_identifier')
            query_ = query_.filter_by(event_id=event.id)
        return query_

    view_kwargs = True
    methods = ['GET', ]
    decorators = (api.has_permission('is_organizer', fetch="event_id", fetch_as="event_id"), )
    schema = StripeAuthorizationSchema
    data_layer = {'session': db.session,
                  'model': StripeAuthorization,
                  'methods': {
                      'query': query
                  }}


class StripeAuthorizationDetail(ResourceDetail):
    """
    Stripe Authorization Detail Resource by ID
    """

    decorators = (api.has_permission('is_coorganizer', fetch="event_id",
                                     fetch_as="event_id", model=StripeAuthorization),)
    schema = StripeAuthorizationSchema
    data_layer = {'session': db.session,
                  'model': StripeAuthorization}


class StripeAuthorizationRelationship(ResourceDetail):
    """
    Stripe Authorization Relationship
    """

    decorators = (api.has_permission('is_coorganizer', fetch="event_id",
                                     fetch_as="event_id", model=StripeAuthorization),)
    schema = StripeAuthorizationSchema
    data_layer = {'session': db.session,
                  'model': StripeAuthorization}
