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
    def before_post(self, args, kwargs, data):
        require_relationship(['event'], data)
        if not has_access('is_coorganizer', event_id=data['event']):
            raise ForbiddenException({'source': ''}, 'Co-organizer access is required.')

    def before_get(self, args, kwargs):
        if 'Authorization' in request.headers and has_access('is_admin'):
            self.schema = TaxSchema
        else:
            self.schema = TaxSchemaPublic

    schema = TaxSchema
    data_layer = {'session': db.session,
                  'model': Tax}


class TaxList(ResourceList):
    def before_get(self, args, view_kwargs):
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
