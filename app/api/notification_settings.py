from flask_rest_jsonapi import ResourceDetail, ResourceList

from app.api.bootstrap import api
from app.api.schema.notification_settings import NotificationSettingSchema
from app.models import db
from app.models.notification_setting import NotificationSettings


class NotificationSettingsList(ResourceList):

    decorators = (api.has_permission('is_admin', methods="GET"),)
    methods = ['GET']
    schema = NotificationSettingSchema
    data_layer = {'session': db.session, 'model': NotificationSettings}


class NotificationSettingsDetail(ResourceDetail):

    schema = NotificationSettingSchema
    decorators = (api.has_permission('is_admin', methods="PATCH"),)
    methods = ['GET', 'PATCH']
    data_layer = {'session': db.session, 'model': NotificationSettings}
