from flask_rest_jsonapi import ResourceDetail, ResourceList
from marshmallow_jsonapi.flask import Schema
from marshmallow_jsonapi import fields

from app.api.bootstrap import api
from app.api.helpers.utilities import dasherize
from app.models import db
from app.models.activity import Activity


class ActivitySchema(Schema):
    """
    Api schema for Activity Model
    """
    class Meta:
        """
        Meta class for Activity Api Schema
        """
        type_ = 'activity'
        self_view = 'v1.activity_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    actor = fields.Str(allow_none=True)
    time = fields.DateTime(allow_none=True)
    action = fields.Str(allow_none=True)


class ActivityList(ResourceList):
    """
    List and create activity
    """
    schema = ActivitySchema
    methods = ['GET', ]
    decorators = (api.has_permission('is_admin', methods="GET"),)
    data_layer = {'session': db.session,
                  'model': Activity}


class ActivityDetail(ResourceDetail):
    """
    Activity detail by id
    """
    schema = ActivitySchema
    methods = ['GET', ]
    decorators = (api.has_permission('is_admin', methods="GET"),)
    data_layer = {'session': db.session,
                  'model': Activity}
