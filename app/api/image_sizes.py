from flask_rest_jsonapi import ResourceDetail, ResourceList

from app.api.bootstrap import api
from app.api.schema.image_sizes import ImageSizeSchema
from app.models import db
from app.models.image_size import ImageSizes


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
    Image_size detail by id
    """
    decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
    schema = ImageSizeSchema
    data_layer = {'session': db.session,
                  'model': ImageSizes}
