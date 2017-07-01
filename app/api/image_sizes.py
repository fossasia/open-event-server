from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields

from app.api.helpers.utilities import dasherize
from app.models import db
from app.api.bootstrap import api
from app.models.image_size import ImageSizes


class ImageSizeSchema(Schema):
    """
    Api schema for image_size Model
    """
    class Meta:
        """
        Meta class for image_size Api Schema
        """
        type_ = 'image-size'
        self_view = 'v1.image_size_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    type = fields.Str()
    full_width = fields.Integer(validate=lambda n: n >= 0)
    full_height = fields.Integer(validate=lambda n: n >= 0)
    full_aspect = fields.Boolean(default=False)
    full_quality = fields.Integer(validate=lambda n: 0 <= n <= 100)
    icon_width = fields.Integer(validate=lambda n: n >= 0)
    icon_height = fields.Integer(validate=lambda n: n >= 0)
    icon_aspect = fields.Boolean(default=False)
    icon_quality = fields.Integer(validate=lambda n: 0 <= n <= 100)
    thumbnail_width = fields.Integer(validate=lambda n: n >= 0)
    thumbnail_height = fields.Integer(validate=lambda n: n >= 0)
    thumbnail_aspect = fields.Boolean(default=False)
    thumbnail_quality = fields.Integer(validate=lambda n: 0 <= n <= 100)
    logo_width = fields.Integer(validate=lambda n: n >= 0)
    logo_height = fields.Integer(validate=lambda n: n >= 0)


class ImageSizeList(ResourceList):
    """
    List and create image_sizes
    """
    decorators = (api.has_permission('is_admin', methods="POST"),)
    schema = ImageSizeSchema
    data_layer = {'session': db.session,
                  'model': ImageSizes}


class ImageSizeDetail(ResourceDetail):
    """
    image_size detail by id
    """
    decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
    schema = ImageSizeSchema
    data_layer = {'session': db.session,
                  'model': ImageSizes}
