from flask_rest_jsonapi import ResourceDetail, ResourceList
from marshmallow_jsonapi.flask import Schema
from marshmallow_jsonapi import fields

from app.api.helpers.utilities import dasherize
from app.models import db
from app.api.bootstrap import api
from app.models.image_config import ImageConfig


class ImageConfigSchema(Schema):
    """
    Api schema for image config Model
    """
    class Meta:
        """
        Meta class for image config Api Schema
        """
        type_ = 'image-config'
        self_view = 'v1.image_config_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    page = fields.Str(required=True)
    size = fields.Str(required=True)


class ImageConfigList(ResourceList):
    """
    List and create image config
    """
    decorators = (api.has_permission('is_admin', methods="POST"),)
    schema = ImageConfigSchema
    data_layer = {'session': db.session,
                  'model': ImageConfig}


class ImageConfigDetail(ResourceDetail):
    """
    Image config detail by id
    """
    decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
    schema = ImageConfigSchema
    data_layer = {'session': db.session,
                  'model': ImageConfig}
