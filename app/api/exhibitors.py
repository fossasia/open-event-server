from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.helpers.errors import ForbiddenError
from app.api.helpers.permission_manager import has_access
from app.api.helpers.query import event_query
from app.api.helpers.utilities import require_relationship
from app.api.schema.exhibitors import ExhibitorSchema
from app.models import db
from app.models.exhibitor import Exhibitor


class ExhibitorListPost(ResourceList):
    def before_post(self, args, kwargs, data):
        require_relationship(['event'], data)
        if not has_access('is_coorganizer', event_id=data['event']):
            raise ForbiddenError(
                {'pointer': '/data/relationships/event'},
                'Co-organizer access is required.',
            )

    methods = ['POST']
    schema = ExhibitorSchema
    data_layer = {'session': db.session, 'model': Exhibitor}


class ExhibitorList(ResourceList):
    def query(self, view_kwargs):
        query_ = Exhibitor.query
        query_ = event_query(query_, view_kwargs)
        return query_

    view_kwargs = True
    methods = ['GET']
    schema = ExhibitorSchema
    data_layer = {'session': db.session, 'model': Exhibitor, 'methods': {'query': query}}


class ExhibitorDetail(ResourceDetail):

    decorators = (
        api.has_permission(
            'is_coorganizer',
            methods="PATCH,DELETE",
            fetch="event_id",
            model=Exhibitor,
        ),
    )
    schema = ExhibitorSchema
    data_layer = {'session': db.session, 'model': Exhibitor}


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
