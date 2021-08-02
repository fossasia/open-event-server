from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound
from sqlalchemy.orm.exc import NoResultFound

from app.api.bootstrap import api
from app.api.helpers.db import get_count, safe_query, safe_query_kwargs
from app.api.helpers.errors import ConflictError, ForbiddenError, MethodNotAllowed
from app.api.helpers.permission_manager import has_access, is_logged_in
from app.api.helpers.utilities import require_relationship
from app.api.schema.tax import TaxSchema, TaxSchemaPublic
from app.models import db
from app.models.event import Event
from app.models.tax import Tax


class TaxList(ResourceList):
    """
    TaxList class for creating a TaxSchema
    only POST and GET method allowed
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
        if not has_access('is_coorganizer', event_id=data['event']):
            raise ForbiddenError({'source': ''}, 'Co-organizer access is required.')
        if (
            get_count(
                db.session.query(Event).filter_by(
                    id=int(data['event']), is_tax_enabled=False
                )
            )
            > 0
        ):
            raise MethodNotAllowed(
                {'parameter': 'event_id'}, "Tax is disabled for this Event"
            )

    def before_create_object(self, data, view_kwargs):
        """
        method to check if tax object already exists for an event
        :param data:
        :param view_kwargs:
        :return:
        """
        if (
            self.session.query(Tax)
            .filter_by(event_id=data['event'], deleted_at=None)
            .first()
        ):
            raise ConflictError(
                {'pointer': '/data/relationships/event'},
                "Tax already exists for this event",
            )

    def before_get(self, args, kwargs):
        """
        method to assign proper schema based on admin access
        :param args:
        :param kwargs:
        :return:
        """
        if is_logged_in() and has_access('is_admin'):
            self.schema = TaxSchema
        else:
            self.schema = TaxSchemaPublic

    methods = ['POST', 'GET']
    view_kwargs = True
    schema = TaxSchema
    data_layer = {
        'session': db.session,
        'model': Tax,
        'methods': {'before_create_object': before_create_object},
    }


class TaxDetail(ResourceDetail):
    """
    Tax details class
    """

    def before_get_object(self, view_kwargs):
        """
        before get method to get the tax id to fetch details
        :param view_kwargs:
        :return:
        """
        event = None
        if view_kwargs.get('event_id'):
            event = safe_query_kwargs(Event, view_kwargs, 'event_id')
        elif view_kwargs.get('event_identifier'):
            event = safe_query_kwargs(
                Event, view_kwargs, 'event_identifier', 'identifier'
            )

        if event:
            tax = safe_query(Tax, 'event_id', event.id, 'event_id')
            view_kwargs['id'] = tax.id

    def before_get(self, args, kwargs):
        """
        before get method to get the resource id for fetching details
        :param args:
        :param kwargs:
        :return:
        """
        if 'id' in kwargs:
            try:
                tax = Tax.query.filter_by(id=kwargs['id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'id'}, f"Tax: Not found for id {id}")
            if is_logged_in() and has_access('is_coorganizer', event_id=tax.event_id):
                self.schema = TaxSchema
            else:
                self.schema = TaxSchemaPublic
        else:
            if is_logged_in() and has_access(
                'is_coorganizer', event_id=kwargs['event_id']
            ):
                self.schema = TaxSchema
            else:
                self.schema = TaxSchemaPublic

    decorators = (
        api.has_permission(
            'is_coorganizer',
            fetch="event_id",
            model=Tax,
            methods="PATCH,DELETE",
        ),
    )
    schema = TaxSchema
    data_layer = {
        'session': db.session,
        'model': Tax,
        'methods': {'before_get_object': before_get_object},
    }


class TaxRelationship(ResourceRelationship):
    """
    Tax Relationship Resource
    """

    decorators = (
        api.has_permission(
            'is_coorganizer',
            fetch="event_id",
            model=Tax,
            methods="PATCH,DELETE",
        ),
    )
    methods = ['GET', 'PATCH']
    schema = TaxSchema
    data_layer = {'session': db.session, 'model': Tax}
