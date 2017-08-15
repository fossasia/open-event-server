from flask_rest_jsonapi import ResourceDetail, ResourceList

from app.api.bootstrap import api
from app.api.schema.activities import ActivitySchema
from app.models import db
from app.models.activity import Activity


class ActivityList(ResourceList):
    """
    List and create activity
    """
    schema = ActivitySchema
    methods = ['GET', ]
    decorators = (api.has_permission('is_admin', ),)
    data_layer = {'session': db.session,
                  'model': Activity}


class ActivityDetail(ResourceDetail):
    """
    Activity detail by id
    """
    schema = ActivitySchema
    methods = ['GET', ]
    decorators = (api.has_permission('is_admin', ),)
    data_layer = {'session': db.session,
                  'model': Activity}
