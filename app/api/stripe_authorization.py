from flask_rest_jsonapi import ResourceDetail, ResourceList
from sqlalchemy.orm.exc import NoResultFound

from app.api.bootstrap import api
from app.api.helpers.db import safe_query
from app.api.helpers.exceptions import ForbiddenException, ConflictException
from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required
from app.api.helpers.utilities import require_relationship
from app.api.schema.stripe_authorization import StripeAuthorizationSchema
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
            raise ForbiddenException({'source': ''}, "Minimum Organizer access required")

    def before_create_object(self, data, view_kwargs):
        """
        method to check if stripe authorization object alredy exists for an event
        :param data:
        :param view_kwargs:
        :return:
        """
        try:
            self.session.query(StripeAuthorization).filter_by(event_id=data['event']).one()
        except NoResultFound:
            pass
        else:
            raise ConflictException({'pointer': '/data/relationships/event'},
                                    "Stripe Authorization already exists for this event")

    schema = StripeAuthorizationSchema
    decorators = (jwt_required, )
    methods = ['POST']
    data_layer = {'session': db.session,
                  'model': StripeAuthorization}


class StripeAuthorizationDetail(ResourceDetail):
    """
    Stripe Authorization Detail Resource by ID
    """
    def before_get_object(self, view_kwargs):
        """
        method to get id of stripe authorization related to an event
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
            view_kwargs['event_id'] = event.id

        if view_kwargs.get('event_id'):
            stripe_authorization = self.session.query(StripeAuthorization).\
                filter_by(event_id=view_kwargs['event_id']).one()
            view_kwargs['id'] = stripe_authorization.id

    decorators = (api.has_permission('is_coorganizer', fetch="event_id",
                                     fetch_as="event_id", model=StripeAuthorization),)
    schema = StripeAuthorizationSchema
    data_layer = {'session': db.session,
                  'model': StripeAuthorization,
                  'methods': {
                      'before_get_object': before_get_object
                  }}


class StripeAuthorizationRelationship(ResourceDetail):
    """
    Stripe Authorization Relationship
    """

    decorators = (api.has_permission('is_coorganizer', fetch="event_id",
                                     fetch_as="event_id", model=StripeAuthorization),)
    schema = StripeAuthorizationSchema
    data_layer = {'session': db.session,
                  'model': StripeAuthorization}
