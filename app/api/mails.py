from flask_rest_jsonapi import ResourceDetail, ResourceList
from marshmallow_jsonapi.flask import Schema
from marshmallow_jsonapi import fields

from app.api.bootstrap import api
from app.api.helpers.utilities import dasherize
from app.models import db
from app.models.mail import Mail


class MailSchema(Schema):
    """
    Api schema for mail Model
    """
    class Meta:
        """
        Meta class for mail Api Schema
        """
        type_ = 'mail'
        self_view = 'v1.mail_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'v1.mail_list'
        inflect = dasherize

    id = fields.Str(dump_only=True)
    recipient = fields.Email(dump_only=True)
    time = fields.DateTime(dump_only=True)
    action = fields.Str(dump_only=True)
    subject = fields.Str(dump_only=True)
    message = fields.Str(dump_only=True)


class MailList(ResourceList):
    """
    List and create mails
    """
    decorators = (api.has_permission('is_admin'),)
    methods = ['GET']
    schema = MailSchema
    data_layer = {'session': db.session,
                  'model': Mail}


class MailDetail(ResourceDetail):
    """
    mail detail by id
    """
    methods = ['GET']
    schema = MailSchema
    decorators = (api.has_permission('is_admin'),)
    data_layer = {'session': db.session,
                  'model': Mail}
