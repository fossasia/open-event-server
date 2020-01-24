from flask_rest_jsonapi import ResourceDetail, ResourceList

from app.api.bootstrap import api
from app.api.schema.mails import MailSchema
from app.models import db
from app.models.mail import Mail


class MailList(ResourceList):
    """
    List and create mails
    """

    decorators = (api.has_permission('is_admin'),)
    methods = ['GET']
    schema = MailSchema
    data_layer = {'session': db.session, 'model': Mail}


class MailDetail(ResourceDetail):
    """
    Mail detail by id
    """

    methods = ['GET']
    schema = MailSchema
    decorators = (api.has_permission('is_admin'),)
    data_layer = {'session': db.session, 'model': Mail}
