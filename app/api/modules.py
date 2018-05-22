from flask_rest_jsonapi import ResourceDetail, ResourceList

from app.api.bootstrap import api
from app.api.schema.modules import ModuleSchema
from app.models import db
from app.models.module import Module


class ModuleList(ResourceList):
    """
    module list
    """
    def before_get(self, *args, **kwargs):
        """
        before get method to get the resource id for fetching details
        :param args:
        :param kwargs:
        :return:
        """
        kwargs['id'] = 1

    decorators = (api.has_permission('is_super_admin', methods=['POST', 'GET'], id="1"),)
    methods = ['GET', 'POST']
    schema = ModuleSchema
    data_layer = {'session': db.session,
                  'model': Module}


class ModuleDetail(ResourceDetail):
    """
    module detail by id
    """
    def before_get(self, args, kwargs):
        """
        before get method to get the resource id for fetching details
        :param args:
        :param kwargs:
        :return:
        """
        kwargs['id'] = 1

    decorators = (api.has_permission('is_admin', methods="PATCH", id="1"),)
    methods = ['GET', 'PATCH']
    schema = ModuleSchema
    data_layer = {'session': db.session,
                  'model': Module}
