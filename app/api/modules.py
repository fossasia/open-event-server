from flask_rest_jsonapi import ResourceDetail

from app.api.bootstrap import api
from app.api.schema.modules import ModuleSchema
from app.models import db
from app.models.module import Module
from app.api.helpers.exceptions import ConflictException

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

    def before_patch(self, args, kwargs, data=None):
        """
        before patch method to verify if admin enables the donations in system
        :param args:
        :param kwargs:
        :param data:
        :return:
        """

    decorators = (api.has_permission('is_admin', methods='PATCH', id='1'),)
    methods = ['GET', 'PATCH']
    schema = ModuleSchema
    data_layer = {'session': db.session,
                  'model': Module,
                  'methods': {'before_patch': before_patch}}
