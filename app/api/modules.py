from flask_rest_jsonapi import ResourceDetail

from app.api.bootstrap import api
from app.api.schema.modules import ModuleSchema
from app.models import db
from app.models.module import Module


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

    decorators = (api.has_permission('is_admin', methods='PATCH', id='1'),)
    methods = ['GET', 'PATCH']
    schema = ModuleSchema
    data_layer = {'session': db.session,
                  'model': Module}
