from flask_rest_jsonapi import ResourceDetail

from app.api.bootstrap import api
from app.api.schema.image_sizes import EventImageSizeSchema
from app.models import db
from app.models.image_size import ImageSizes


class EventImageSizeDetail(ResourceDetail):
    """
    Event Image_size detail by id
    """

    @classmethod
    def before_get(self, args, kwargs):
        kwargs['id'] = 1

    decorators = (api.has_permission('is_admin', methods='PATCH', id="1"),)
    methods = ['GET', 'PATCH']
    schema = EventImageSizeSchema
    data_layer = {'session': db.session, 'model': ImageSizes}
