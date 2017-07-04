from flask_rest_jsonapi import ResourceDetail
from marshmallow_jsonapi.flask import Schema
from marshmallow_jsonapi import fields

from app.api.helpers.utilities import dasherize
from app.models import db
from app.models.module import Module
from app.api.bootstrap import api


class ModuleSchema(Schema):
    """
    Admin Api schema for modules Model
    """
    class Meta:
        """
        Meta class for module Api Schema
        """
        type_ = 'module'
        self_view = 'v1.module_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    ticket_include = fields.Boolean(default=False)
    payment_include = fields.Boolean(default=False)
    donation_include = fields.Boolean(default=False)


class ModuleDetail(ResourceDetail):
    """
    module detail by id
    """
    def before_get(self, args, kwargs):
        kwargs['id'] = 1

    decorators = (api.has_permission('is_admin', methods="PATCH", id="1"),)
    methods = ['GET', 'PATCH']
    schema = ModuleSchema
    data_layer = {'session': db.session,
                  'model': Module}
