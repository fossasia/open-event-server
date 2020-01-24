from flask_rest_jsonapi import ResourceDetail, ResourceList

from app.api.bootstrap import api
from app.api.schema.message_settings import MessageSettingSchema
from app.models import db
from app.models.message_setting import MessageSettings


class MessageSettingsList(ResourceList):
    """
    List Events Role Permission
    """

    def query(self, view_kwargs):
        """
        query method for Message Setting List
        :param view_kwargs:
        :return:
        """
        query_ = db.session.query(MessageSettings).order_by(MessageSettings.id)
        return query_

    decorators = (api.has_permission('is_admin', methods="GET"),)
    methods = ['GET']
    schema = MessageSettingSchema
    data_layer = {
        'session': db.session,
        'model': MessageSettings,
        'methods': {'query': query},
    }


class MessageSettingsDetail(ResourceDetail):
    """
    Events Role Permission detail by id
    """

    schema = MessageSettingSchema
    decorators = (api.has_permission('is_admin', methods="PATCH"),)
    methods = ['GET', 'PATCH']
    data_layer = {'session': db.session, 'model': MessageSettings}
