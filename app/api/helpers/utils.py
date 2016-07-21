import json
from hashlib import md5

from flask import request
from flask.ext.restplus import Resource as RestplusResource
from flask_restplus import Model, fields, reqparse

from .helpers import get_object_list, get_object_or_404, get_object_in_event, \
    create_model, validate_payload, delete_model, update_model, \
    handle_extra_payload, get_paginated_list
from app.models.event import Event as EventModel
from .error_docs import (
    notfound_error_model,
    notauthorized_error_model,
    validation_error_model,
    invalidservice_error_model,
)

DEFAULT_PAGE_START = 1
DEFAULT_PAGE_LIMIT = 20

POST_RESPONSES = {
    400: ('Validation error', validation_error_model),
    401: ('Authentication failure', notauthorized_error_model),
    404: ('Event does not exist', notfound_error_model),
    201: 'Resource created successfully'
}

PUT_RESPONSES = {
    400: ('Validation Error', validation_error_model),
    401: ('Authentication failure', notauthorized_error_model),
    404: ('Object/Event not found', notfound_error_model)
}

SERVICE_RESPONSES = {
    404: ('Service not found', notfound_error_model),
    400: ('Service does not belong to event', invalidservice_error_model),
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


# Custom Resource Class
class Resource(RestplusResource):
    def dispatch_request(self, *args, **kwargs):
        resp = super(Resource, self).dispatch_request(*args, **kwargs)

        # ETag checking.
        # Check only for GET requests, for now.
        if request.method == 'GET':
            old_etag = request.headers.get('If-None-Match', '')
            # Generate hash
            data = json.dumps(resp)
            new_etag = md5(data).hexdigest()

            if new_etag == old_etag:
                # Resource has not changed
                return '', 304
            else:
                # Resource has changed, send new ETag value
                return resp, 200, {'ETag': new_etag}

        return resp


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

    def list(self, **kwargs):
        return get_object_list(self.model, **kwargs)

    def paginated_list(self, url=None, args={}, **kwargs):
        return get_paginated_list(self.model, url=url, args=args, **kwargs)

    def create(self, data, validate=True):
        if validate:
            data = self.validate(data, self.post_api_model)
        item = create_model(self.model, data)
        return item

    def update(self, id_, data, validate=True):
        if validate:
            data = self.validate_put(data, self.put_api_model)
        item = update_model(self.model, id_, data)
        return item

    def delete(self, id_):
        item = delete_model(self.model, id_)
        return item

    def validate(self, data, model=None, check_required=True):
        if not model:
            model = self.post_api_model
        if model:
            data = handle_extra_payload(data, model)
            validate_payload(data, model, check_required=check_required)
        return data

    def validate_put(self, data, model=None):
        """
        Abstraction over validate with check_required set to False
        """
        return self.validate(data, model=model, check_required=False)

    # Helper functions
    def _del(self, data, fields):
        """
        Safe delete fields from payload
        """
        data_copy = data.copy()
        for field in fields:
            if field in data:
                del data_copy[field]
        return data_copy


# DAO for Service Models
class ServiceDAO(BaseDAO):
    """
    Data Access Object for service models like microlocations,
    speakers and so.
    """
    def get(self, event_id, sid):
        return get_object_in_event(self.model, sid, event_id)

    def list(self, event_id, **kwargs):
        # Check if an event with `event_id` exists
        get_object_or_404(EventModel, event_id)
        return get_object_list(self.model, event_id=event_id, **kwargs)

    def paginated_list(self, url=None, args={}, **kwargs):
        return get_paginated_list(self.model, url=url, args=args, **kwargs)

    def create(self, event_id, data, url, validate=True):
        if validate:
            data = self.validate(data)
        item = create_model(self.model, data, event_id=event_id)

        # Return created resource with a 201 status code and its Location
        # (url) in the header.
        resource_location = url + '/' + str(item.id)
        return item, 201, {'Location': resource_location}

    def update(self, event_id, service_id, data, validate=True):
        if validate:
            data = self.validate_put(data)
        item = update_model(self.model, service_id, data, event_id)
        return item

    def delete(self, event_id, service_id):
        item = delete_model(self.model, service_id, event_id=event_id)
        return item

# store task results in case of testing
# state and info
TASK_RESULTS = {}
