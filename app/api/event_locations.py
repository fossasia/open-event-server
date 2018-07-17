from flask_rest_jsonapi import ResourceList

from app.api.bootstrap import api
from app.api.schema.event_locations import EventLocationSchema
from app.models import db
from app.models.event_location import EventLocation


class EventLocationList(ResourceList):

    """
    List event locations
    """
    decorators = (api.has_permission('is_admin', methods="POST"),)
    schema = EventLocationSchema
    data_layer = {'session': db.session,
                  'model': EventLocation}
