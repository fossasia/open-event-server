from flask_rest_jsonapi import ResourceDetail
from flask import request
from flask_jwt import current_identity as current_user, _jwt_required
from flask import current_app as app

from app.api.bootstrap import api
from app.api.schema.modules import ModuleSchemaAdmin
from app.models import db
from app.models.module import Module
from app.api.helpers.exceptions import ForbiddenException


class ModuleDetail(ResourceDetail):
    """
    setting detail by id
    """

    def before_get(self, args, kwargs):
        kwargs['id'] = 1

        if 'Authorization' in request.headers:
            _jwt_required(app.config['JWT_DEFAULT_REALM'])

            if current_user.is_admin or current_user.is_super_admin:
                self.schema = ModuleSchemaAdmin
            else:
                raise ForbiddenException(
                    {'pointer': '/data/attributes'}, "Access Forbidden"
                )
        else:
            raise ForbiddenException(
                {'pointer': '/data/attributes'}, "Authorization Required"
            )

    decorators = (api.has_permission('is_admin', methods='PATCH', id='1'),)
    methods = ['GET', 'PATCH']
    schema = ModuleSchemaAdmin
    data_layer = {'session': db.session,
                  'model': Module}
