from flask import current_app as app
from flask import jsonify, request, Blueprint, make_response
from flask_jwt_extended import verify_jwt_in_request, current_user
from flask_rest_jsonapi import ResourceDetail

from app.api.bootstrap import api
from app.api.schema.settings import SettingSchemaAdmin, SettingSchemaNonAdmin, SettingSchemaPublic
from app.models import db
from app.models.setting import Setting
from app.settings import refresh_settings
from app.api.helpers.mail import send_test_email
from app.api.helpers.errors import UnprocessableEntityError
from app.api.helpers.permissions import is_admin


admin_misc_routes = Blueprint('admin_misc', __name__, url_prefix='/v1')


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
            verify_jwt_in_request()

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


@admin_misc_routes.route('/test-mail', methods=['POST'])
@is_admin
def test_email_setup():
    recipient = request.json.get('recipient')
    if not recipient:
        return UnprocessableEntityError({'source': 'recipient'},
                                        'Required parameter recipient not found').respond()
    send_test_email(recipient)
    return make_response(jsonify(message='Test mail sent, please verify delivery'), 200)
