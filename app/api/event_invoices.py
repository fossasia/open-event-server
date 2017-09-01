from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.helpers.db import safe_query
from app.api.helpers.permissions import is_admin
from app.api.helpers.query import event_query
from app.api.helpers.utilities import require_relationship
from app.api.schema.event_invoices import EventInvoiceSchema
from app.models import db
from app.models.discount_code import DiscountCode
from app.models.event_invoice import EventInvoice
from app.models.user import User


class EventInvoiceList(ResourceList):
    """
    List and Create Event Invoices
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

    def query(self, view_kwargs):
        """
        query method for event invoice list
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(EventInvoice)
        query_ = event_query(self, query_, view_kwargs)
        if view_kwargs.get('user_id'):
            user = safe_query(self, User, 'id', view_kwargs['user_id'], 'user_id')
            query_ = query_.join(User).filter(User.id == user.id)
        if view_kwargs.get('discount_code_id'):
            discount_code = safe_query(self, DiscountCode, 'id', view_kwargs['discount_code_id'], 'discount_code_id')
            query_ = query_.join(DiscountCode).filter(DiscountCode.id == discount_code.id)
        return query_

    view_kwargs = True
    methods = ['GET', ]
    decorators = (api.has_permission('is_organizer', ), )
    schema = EventInvoiceSchema
    data_layer = {'session': db.session,
                  'model': EventInvoice,
                  'methods': {
                      'query': query
                  }}


class EventInvoiceDetail(ResourceDetail):
    """
    Event Invoice detail by id
    """
    decorators = (is_admin,)
    schema = EventInvoiceSchema
    data_layer = {'session': db.session,
                  'model': EventInvoice}


class EventInvoiceRelationshipRequired(ResourceRelationship):
    """
    Event Invoice Relationship for required entities
    """
    decorators = (is_admin,)
    methods = ['GET', 'PATCH']
    schema = EventInvoiceSchema
    data_layer = {'session': db.session,
                  'model': EventInvoice}


class EventInvoiceRelationshipOptional(ResourceRelationship):
    """
    Event Invoice Relationship
    """
    decorators = (is_admin,)
    schema = EventInvoiceSchema
    data_layer = {'session': db.session,
                  'model': EventInvoice}
