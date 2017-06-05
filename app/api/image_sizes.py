from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from app.models import db
from app.api.helpers.permissions import jwt_required, is_admin, is_user_itself
from sqlalchemy.orm.exc import NoResultFound
from flask_rest_jsonapi.exceptions import ObjectNotFound
from app.models.event import Event
from app.models.image_size import ImageSizes


class ImageSizeSchema(Schema):
    """
    Api schema for image_size Model
    """
    class Meta:
        """
        Meta class for image_size Api Schema
        """
        type_ = 'image_size'
        self_view = 'v1.image_size_detail'
        self_view_kwargs = {'id': '<id>'}

    id = fields.Str(dump_only=True)
    type = fields.Str()
    full_width = fields.Integer()
    full_height = fields.Integer()
    full_aspect = fields.Str()
    full_quality = fields.Integer()
    icon_width = fields.Integer()
    icon_height = fields.Integer()
    icon_aspect = fields.Str()
    icon_quality = fields.Integer()
    thumbnail_width = fields.Integer()
    thumbnail_height = fields.Integer()
    thumbnail_aspect = fields.Str()
    thumbnail_quality = fields.Integer()
    logo_width = fields.Integer()
    logo_height = fields.Integer()


class ImageSizeList(ResourceList):
    """
    List and create image_sizes
    """
    post = is_admin(ResourceList.post.__func__)
    schema = ImageSizeSchema
    data_layer = {'session': db.session,
                  'model': ImageSizes}


class ImageSizeDetail(ResourceDetail):
    """
    image_size detail by id
    """
    patch = is_admin(ResourceDetail.patch.__func__)
    delete = is_admin(ResourceDetail.delete.__func__)
    schema = ImageSizeSchema
    data_layer = {'session': db.session,
                  'model': ImageSizes}
