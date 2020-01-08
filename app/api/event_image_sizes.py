from flask_rest_jsonapi import ResourceDetail

from app.api.bootstrap import api
from app.api.schema.image_sizes import EventImageSizeSchema
from app.models import db
from app.models.image_size import ImageSizes
from app.api.helpers import db as db_helper

class EventImageSizeDetail(ResourceDetail):
    """
    Event Image_size detail by type
    """
    @classmethod
    def before_patch(self, args, kwargs, data=None):
        # overrides the patch request id by image size type
        event_image_size, is_created = db_helper.get_or_create(ImageSizes, type='event-image')
        if is_created:
            event_image_size.init_event_image_size()
            db.session.commit()
        kwargs['id'] = event_image_size.id

    @classmethod
    def before_get(self, args, kwargs):
        event_image_size, is_created = db_helper.get_or_create(ImageSizes, type='event-image')
        if is_created:
            event_image_size.init_event_image_size()
            db.session.commit()
        kwargs['id'] = event_image_size.id
    decorators = (api.has_permission('is_admin', methods='PATCH', id="1"),)
    methods = ['GET', 'PATCH']
    schema = EventImageSizeSchema
    data_layer = {'session': db.session,
                  'model': ImageSizes}
