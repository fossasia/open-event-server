from flask_restplus import Model, fields, reqparse
from .helpers import get_object_list, get_object_or_404, get_object_in_event, \
    create_model, validate_payload, delete_model, update_model
from open_event.models.event import Event as EventModel

DEFAULT_PAGE_START = 1
DEFAULT_PAGE_LIMIT = 20

POST_RESPONSES = {
    400: 'Validation error',
    401: 'Authentication failure',
    404: 'Event does not exist',
    201: 'Resource created successfully'
}

PUT_RESPONSES = {
    400: 'Validation Error / Bad request',
    401: 'Authentication failure',
    404: 'Object/Event not found'
}

# Parameters for a paginated response
PAGE_PARAMS = {
    'start': {
        'description': 'Serial number to start from',
        'type': int,
        'default': DEFAULT_PAGE_START
    },
    'limit': {
        'description': 'Limit on the number of results',
        'type': int,
        'default': DEFAULT_PAGE_LIMIT
    },
}

# Base Api Model for a paginated response
PAGINATED_MODEL = Model('PaginatedModel', {
    'start': fields.Integer,
    'limit': fields.Integer,
    'count': fields.Integer,
    'next': fields.String,
    'previous': fields.String
})


# Base class for Paginated Resource
class PaginatedResourceBase():
    """
    Paginated Resource Helper class
    This includes basic properties used in the class
    """
    parser = reqparse.RequestParser()
    parser.add_argument('start', type=int, default=DEFAULT_PAGE_START)
    parser.add_argument('limit', type=int, default=DEFAULT_PAGE_LIMIT)


# DAO for Models
class BaseDAO:
    """
    DAO for a basic independent model
    """
    def __init__(self, model, post_api_model=None, put_api_model=None):
        self.model = model
        self.post_api_model = post_api_model
        self.put_api_model = put_api_model if put_api_model else post_api_model

    def get(self, id_):
        return get_object_or_404(self.model, id_)

    def list(self):
        return get_object_list(self.model)

    def create(self, data, validate=True):
        if validate:
            self.validate(data, self.post_api_model)
        item = create_model(self.model, data)
        return item

    def update(self, id_, data, validate=True):
        if validate:
            self.validate(data, self.put_api_model)
        item = update_model(self.model, id_, data)
        return item

    def delete(self, id_):
        item = delete_model(self.model, id_)
        return item

    def validate(self, data, model=None):
        if not model:
            model = self.post_api_model
        if model:
            validate_payload(data, model)


# DAO for Service Models
class ServiceDAO(BaseDAO):
    """
    Data Access Object for service models like microlocations,
    speakers and so.
    """
    def get(self, event_id, sid):
        return get_object_in_event(self.model, sid, event_id)

    def list(self, event_id):
        # Check if an event with `event_id` exists
        get_object_or_404(EventModel, event_id)
        return get_object_list(self.model, event_id=event_id)

    def create(self, event_id, data, url, validate=True):
        if validate:
            self.validate(data)
        item = create_model(self.model, data, event_id=event_id)

        # Return created resource with a 201 status code and its Location
        # (url) in the header.
        resource_location = url + '/' + str(item.id)
        return item, 201, {'Location': resource_location}

    def update(self, event_id, service_id, data, validate=True):
        if validate:
            self.validate(data)
        item = update_model(self.model, service_id, data, event_id)
        return item

    def delete(self, event_id, service_id):
        item = delete_model(self.model, service_id, event_id=event_id)
        return item
