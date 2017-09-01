from flask import request
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound
from sqlalchemy.orm.exc import NoResultFound

from app.api.bootstrap import api
from app.api.helpers.exceptions import ForbiddenException
from app.api.helpers.permission_manager import has_access
from app.api.helpers.query import event_query
from app.api.helpers.utilities import require_relationship
from app.api.schema.tax import TaxSchemaPublic, TaxSchema
from app.models import db
from app.models.tax import Tax


class TaxListPost(ResourceList):
    """
    TaxListPost class for TaxSchema
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
            raise ForbiddenException({'source': ''}, 'Co-organizer access is required.')

    def before_get(self, args, kwargs):
        """
        method to assign proper schema based on admin access
        :param args:
        :param kwargs:
        :return:
        """
        if 'Authorization' in request.headers and has_access('is_admin'):
            self.schema = TaxSchema
        else:
            self.schema = TaxSchemaPublic

    schema = TaxSchema
    data_layer = {'session': db.session,
                  'model': Tax}


class TaxList(ResourceList):
    """
    TaxList class for TaxSchema
    """
    def before_get(self, args, view_kwargs):
        """
        before get method to get the resource id for assigning schema
        :param args:
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('event_identifier'):
            try:
                event = Tax.query.filter_by(identifier=view_kwargs['id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'event_identifier'},
                                     "Event: {} not found".format(view_kwargs['event_identifier']))
            else:
                view_kwargs['event_id'] = event.id

        if has_access('is_coorganizer', event_id=view_kwargs['event_id']):
            self.schema = TaxSchema
        else:
            self.schema = TaxSchemaPublic

    def query(self, view_kwargs):
        """
        query method for resource list
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(Tax)
        query_ = event_query(self, query_, view_kwargs)
        return query_

    view_kwargs = True
    methods = ['GET', ]
    schema = TaxSchema
    data_layer = {'session': db.session,
                  'model': Tax,
                  'methods': {
                      'query': query
                  }}


class TaxDetail(ResourceDetail):
    """
     tax detail by id
    """

    def before_get(self, args, kwargs):
        """
        before get method to get the resource id for fetching details
        :param args:
        :param kwargs:
        :return:
        """
        tax = Tax.query.filter_by(id=kwargs['id']).one()
        if 'Authorization' in request.headers and has_access('is_coorganizer', event_id=tax.event_id):
            self.schema = TaxSchema
        else:
            self.schema = TaxSchemaPublic

    decorators = (api.has_permission('is_coorganizer', fetch="event_id",
                                     fetch_as="event_id", model=Tax, methods="PATCH,DELETE"),)
    schema = TaxSchema
    data_layer = {'session': db.session,
                  'model': Tax}


class TaxRelationship(ResourceRelationship):
    """
        Tax Relationship Resource
    """
    decorators = (api.has_permission('is_coorganizer', fetch="event_id",
                                     fetch_as="event_id", model=Tax, methods="PATCH,DELETE"),)
    methods = ['GET', 'PATCH']
    schema = TaxSchema
    data_layer = {'session': db.session,
                  'model': Tax}
