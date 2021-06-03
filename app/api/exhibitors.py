from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.helpers.db import safe_query_kwargs
from app.api.helpers.errors import ForbiddenError
from app.api.helpers.permission_manager import has_access
from app.api.helpers.query import event_query
from app.api.helpers.utilities import changed, require_relationship
from app.api.schema.exhibitors import ExhibitorSchema
from app.models import db
from app.models.exhibitor import Exhibitor
from app.models.session import Session


class ExhibitorListPost(ResourceList):
    def before_post(self, args, kwargs, data):
        require_relationship(['event'], data)
        if not has_access('is_coorganizer', event_id=data['event']):
            raise ForbiddenError(
                {'pointer': '/data/relationships/event'},
                'Co-organizer access is required.',
            )

    def after_create_object(self, exhibitor, data, view_kwargs):
        if data.get('banner_url'):
            start_image_resizing_tasks(exhibitor, data['banner_url'])

    methods = ['POST']
    schema = ExhibitorSchema
    data_layer = {
        'session': db.session,
        'model': Exhibitor,
        'methods': {'after_create_object': after_create_object},
    }


class ExhibitorList(ResourceList):
    def query(self, view_kwargs):
        query_ = Exhibitor.query
        if view_kwargs.get('session_id'):
            session = safe_query_kwargs(Session, view_kwargs, 'session_id')
            # session-exhibitor :: many-to-many relationship
            query_ = Exhibitor.query.filter(Exhibitor.sessions.any(id=session.id))
        elif view_kwargs.get('event_id') or view_kwargs.get('event_identifier'):
            query_ = event_query(query_, view_kwargs)
        return query_

    view_kwargs = True
    methods = ['GET']
    schema = ExhibitorSchema
    data_layer = {
        'session': db.session,
        'model': Exhibitor,
        'methods': {'query': query},
    }


class ExhibitorDetail(ResourceDetail):
    def before_update_object(self, exhibitor, data, view_kwargs):
        if changed(exhibitor, data, 'banner_url'):
            start_image_resizing_tasks(exhibitor, data['banner_url'])

    decorators = (
        api.has_permission(
            'is_coorganizer',
            methods="PATCH,DELETE",
            fetch="event_id",
            model=Exhibitor,
        ),
    )
    schema = ExhibitorSchema
    data_layer = {
        'session': db.session,
        'model': Exhibitor,
        'methods': {
            'before_update_object': before_update_object,
        },
    }


class ExhibitorRelationship(ResourceRelationship):

    decorators = (
        api.has_permission(
            'is_coorganizer',
            methods="PATCH,DELETE",
            fetch="event_id",
            model=Exhibitor,
        ),
    )
    methods = ['GET', 'PATCH']
    schema = ExhibitorSchema
    data_layer = {'session': db.session, 'model': Exhibitor}


def start_image_resizing_tasks(exhibitor, original_image_url):
    exhibitor_id = str(exhibitor.id)
    from .helpers.tasks import resize_exhibitor_images_task

    resize_exhibitor_images_task.delay(exhibitor_id, original_image_url)
