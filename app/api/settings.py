from flask import current_app as app
from flask import request
from flask_jwt import current_identity as current_user, _jwt_required
from flask_rest_jsonapi import ResourceDetail

from app.api.bootstrap import api
from app.api.schema.settings import SettingSchemaAdmin, SettingSchemaNonAdmin, SettingSchemaPublic
from app.models import db
from app.models.setting import Setting
from app.settings import refresh_settings


class Environment:

    def __init__(self):
        pass

    DEVELOPMENT = 'development'
    STAGING = 'staging'
    PRODUCTION = 'production'
    TESTING = 'testing'


class SettingDetail(ResourceDetail):
    """
    setting detail by id
    """

    def before_get(self, args, kwargs):
        refresh = request.args.get('refresh')
        if refresh == 'true':
            refresh_settings()
        kwargs['id'] = 1

        if 'Authorization' in request.headers:
            _jwt_required(app.config['JWT_DEFAULT_REALM'])

            if current_user.is_admin or current_user.is_super_admin:
                self.schema = SettingSchemaAdmin
            else:
                self.schema = SettingSchemaNonAdmin
        else:
            self.schema = SettingSchemaPublic

    decorators = (api.has_permission('is_admin', methods="PATCH", id="1"),)
    methods = ['GET', 'PATCH']
    schema = SettingSchemaAdmin
    data_layer = {'session': db.session,
                  'model': Setting}

    def after_patch(self, result):
        # Update settings cache after PATCH
        refresh_settings()
