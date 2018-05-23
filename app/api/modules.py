from flask_rest_jsonapi import ResourceDetail
from flask import request
from flask_jwt import _jwt_required
from flask import current_app as app

from app.api.bootstrap import api
from app.api.schema.modules import ModuleSchema
from app.models import db
from app.models.module import Module
from app.api.helpers.exceptions import ForbiddenException


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

        if 'Authorization' in request.headers:
            _jwt_required(app.config['JWT_DEFAULT_REALM'])
        else:
            raise ForbiddenException(
                {'pointer': '/data/attributes'}, "Authorization Required"
            )

    decorators = (api.has_permission('is_admin', methods='PATCH', id='1'),)
    methods = ['GET', 'PATCH']
    schema = ModuleSchema
    data_layer = {'session': db.session,
                  'model': Module}
