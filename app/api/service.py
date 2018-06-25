from flask_rest_jsonapi import ResourceDetail, ResourceList

from app.api.bootstrap import api
from app.api.schema.services import ServiceSchema
from app.models import db
from app.models.service import Service


class ServiceList(ResourceList):
    """
    List all services i.e. microlocation, session, speaker, track, sponsor
    """
    decorators = (api.has_permission('is_admin', methods="GET"),)
    methods = ['GET']
    schema = ServiceSchema
    data_layer = {'session': db.session,
                  'model': Service}


class ServiceDetail(ResourceDetail):
    """
    service detail by id
    """
    decorators = (api.has_permission('is_admin', methods="PATCH"),)
    schema = ServiceSchema
    methods = ['GET', 'PATCH']
    data_layer = {'session': db.session,
                  'model': Service}
