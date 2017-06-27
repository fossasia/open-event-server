from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields

from app.api.bootstrap import api
from app.api.helpers.utilities import dasherize
from app.models import db
from app.api.helpers.permissions import is_admin
from app.models.page import Page


class PageSchema(Schema):
    """
    Api schema for page Model
    """
    class Meta:
        """
        Meta class for page Api Schema
        """
        type_ = 'page'
        self_view = 'v1.page_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    title = fields.Str()
    url = fields.String(required=True)
    description = fields.Str()
    place = fields.Str()
    language = fields.Str()
    index = fields.Integer(default=0)


class PageList(ResourceList):
    """
    List and create page
    """
    decorators = (api.has_permission('is_admin', methods="POST"),)
    schema = PageSchema
    data_layer = {'session': db.session,
                  'model': Page}


class PageDetail(ResourceDetail):
    """
    Page detail by id
    """
    schema = PageSchema
    decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
    data_layer = {'session': db.session,
                  'model': Page}
