from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.helpers.db import safe_query_kwargs
from app.api.helpers.errors import ForbiddenError
from app.api.helpers.permission_manager import has_access
from app.api.helpers.query import event_query
from app.api.helpers.utilities import require_relationship
from app.api.schema.faq_types import FaqTypeSchema
from app.models import db
from app.models.faq import Faq
from app.models.faq_type import FaqType


class FaqTypeListPost(ResourceList):
    """
    List and create faq-types
    """

    def before_post(self, args, kwargs, data):
        require_relationship(['event'], data)

        if not has_access('is_coorganizer', event_id=data['event']):
            raise ForbiddenError({'source': ''}, 'Co-organizer access is required.')

    methods = [
        'POST',
    ]
    schema = FaqTypeSchema
    data_layer = {'session': db.session, 'model': FaqType}


class FaqTypeList(ResourceList):
    """
    List faq-types
    """

    def query(self, view_kwargs):
        """
        query method for Session Type List
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(FaqType)
        query_ = event_query(query_, view_kwargs)
        return query_

    view_kwargs = True
    methods = [
        'GET',
    ]
    schema = FaqTypeSchema
    data_layer = {
        'session': db.session,
        'model': FaqType,
        'methods': {
            'query': query,
        },
    }


class FaqTypeDetail(ResourceDetail):
    """
    Detail about a single faq type by id
    """

    def before_get_object(self, view_kwargs):
        """
        before get method for session type detail
        :param data:
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('faq_id'):
            faq = safe_query_kwargs(Faq, view_kwargs, 'faq_id')
            if faq.faq_type_id:
                view_kwargs['id'] = faq.faq_type_id
            else:
                view_kwargs['id'] = None

    decorators = (
        api.has_permission(
            'is_coorganizer',
            methods="PATCH,DELETE",
            fetch="event_id",
            model=FaqType,
        ),
    )
    schema = FaqTypeSchema
    data_layer = {
        'session': db.session,
        'model': FaqType,
        'methods': {'before_get_object': before_get_object},
    }


class FaqTypeRelationshipRequired(ResourceRelationship):
    """
    FaqType Relationship
    """

    methods = ['GET', 'PATCH']
    decorators = (
        api.has_permission(
            'is_coorganizer',
            methods="PATCH,DELETE",
            fetch="event_id",
            model=FaqType,
        ),
    )
    schema = FaqTypeSchema
    data_layer = {'session': db.session, 'model': FaqType}


class FaqTypeRelationshipOptional(ResourceRelationship):
    """
    FaqType Relationship
    """

    decorators = (
        api.has_permission(
            'is_coorganizer',
            methods="PATCH,DELETE",
            fetch="event_id",
            model=FaqType,
        ),
    )
    schema = FaqTypeSchema
    data_layer = {'session': db.session, 'model': FaqType}
