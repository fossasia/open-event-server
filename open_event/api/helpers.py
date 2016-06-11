from functools import wraps
from flask import request, g
from flask.ext.restplus import abort
from flask.ext import login
from flask.ext.scrypt import check_password_hash
from flask_jwt import jwt_required, JWTError, current_identity

from open_event.models.event import Event as EventModel
from open_event.models import db
from custom_fields import CustomField
from open_event.models.user import User as UserModel
from open_event.helpers.data import save_to_db, update_version, delete_from_db


def _error_abort(code, message):
    """Abstraction over restplus `abort`.
    Returns error with the status code and message.
    """
    error = {
        'code': code,
        'message': message
    }
    abort(code, error=error)


def _get_queryset(klass):
    """Returns the queryset for `klass` model"""
    return klass.query


def _make_url_query(args):
    """
    Helper function to return a query url string from a dict
    """
    return '?' + '&'.join('%s=%s' % (key, args[key]) for key in args)


def get_object_list(klass, **kwargs):
    """Returns a list of objects of a model class. Uses other passed arguments
    with `filter_by` to filter objects.
    `klass` can be a model such as a Track, Event, Session, etc.
    """
    queryset = _get_queryset(klass)
    obj_list = list(queryset.filter_by(**kwargs))
    return obj_list


def get_list_or_404(klass, **kwargs):
    """Abstraction over `get_object_list`.
    Raises 404 error if the `obj_list` is empty.
    """
    obj_list = get_object_list(klass, **kwargs)
    if not obj_list:
        _error_abort(404, 'Object list is empty')
    return obj_list


def get_object_or_404(klass, id_):
    """Returns a specific object of a model class given its identifier. In case
    the object is not found, 404 is returned.
    `klass` can be a model such as a Track, Event, Session, etc.
    """
    queryset = _get_queryset(klass)
    obj = queryset.get(id_)
    if obj is None:
        _error_abort(404, '{} does not exist'.format(klass.__name__))
    return obj


def get_object_in_event(klass, id_, event_id):
    """Returns an object (such as a Session, Track, Speaker, etc.) belonging
    to an Event.

    First checks if Event with `event_id` exists. Then checks if  model `klass`
    (e.g. Track) with `id_` exists.
    If both exist, it checks if model belongs to that Event. If it doesn't,
    it returns a 400 (Bad Request) status.
    """
    event = get_object_or_404(EventModel, event_id)
    obj = get_object_or_404(klass, id_)

    if obj.event_id != event.id:
        _error_abort(400, 'Object does not belong to event')

    return obj


def get_paginated_list(klass, url, args={}, **kwargs):
    """
    Returns a paginated response object

    klass - model class to query from
    url - url of the request
    args - args passed to the request as query parameters
    kwargs - filters for query on the `klass` model. if
        kwargs has event_id, check if it exists for 404
    """
    if 'event_id' in kwargs:
        get_object_or_404(EventModel, kwargs['event_id'])
    # get page bounds
    start = args['start']
    limit = args['limit']
    # check if page exists
    results = get_object_list(klass, **kwargs)
    count = len(results)
    if (count < start):
        abort(404, 'Start position (%s) out of bound' % start)
    # make response
    obj = {}
    obj['start'] = start
    obj['limit'] = limit
    obj['count'] = count
    # make URLs
    # make previous url
    args_copy = args.copy()
    if start == 1:
        obj['previous'] = ''
    else:
        args_copy['start'] = max(1, start - limit)
        args_copy['limit'] = start - 1
        obj['previous'] = url + _make_url_query(args_copy)
    # make next url
    args_copy = args.copy()
    if start + limit > count:
        obj['next'] = ''
    else:
        args_copy['start'] = start + limit
        obj['next'] = url + _make_url_query(args_copy)
    # finally extract result according to bounds
    obj['results'] = results[(start - 1):(start - 1 + limit)]

    return obj


def validate_payload(payload, api_model):
    """
    Validate payload against an api_model. Aborts in case of failure
    - This function is for custom fields as they can't be validated by
      flask restplus automatically.
    - This is to be called at the start of a post or put method
    """
    for key in payload:
        field = api_model[key]
        if isinstance(field, CustomField) and hasattr(field, 'validate'):
            if not field.validate(payload[key]):
                _error_abort(400, 'Validation of \'%s\' field failed' % key)


def save_db_model(new_model, model_name, event_id=None):
    """
    Save a new/modified model to database
    """
    save_to_db(new_model, "Model %s saved" % model_name)
    if not event_id:
        update_version(event_id, False, "session_ver")
    return new_model


def create_service_model(model, event_id, data):
    """
    Create a new service model (microlocations, sessions, speakers etc)
    and save it to database
    """
    get_object_or_404(EventModel, event_id)
    data['event_id'] = event_id
    new_model = model(**data)
    save_to_db(new_model, "Model %s saved" % model.__name__)
    update_version(event_id, False, "session_ver")
    return new_model


def delete_service_model(model, event_id, service_id):
    """
    Delete a service model.
    """
    item = get_object_in_event(model, service_id, event_id)
    delete_from_db(item, '{} deleted'.format(model.__name__))
    return item


def update_model(model, item_id, data, event_id=None):
    """
    Updates a model
    """
    if event_id is not None:
        item = get_object_in_event(model, item_id, event_id)
    else:
        item = get_object_or_404(model, item_id)
    db.session.query(model).filter_by(id=item_id).update(dict(data))
    # model.__table__.update().where(model.id==item_id).values(**data)
    save_to_db(item, "%s updated" % model.__name__)
    if event_id:
        update_version(event_id, False, "session_ver")
    return item


def requires_auth(f):
    """
    Custom decorator to restrict non-login access to views
    g.user holds the successfully authenticated user
    Allows JWT token based access and Basic auth access
    Falls back to active session if both are not present
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        message = 'Authentication credentials not found'
        success = False
        # JWT Auth
        try:
            auth_jwt()
            success = True
        except JWTError as e:
            if e.headers is not None and 'WWW-Authenticate' not in e.headers:
                # JWT header was set but something wrong happened
                _error_abort(401, e.error + ': ' + e.description)

        # Basic Auth
        if not success:
            results = auth_basic()
            if not results[0]:
                if results[1]:  # basic auth was set but..
                    _error_abort(401, results[1])
            else:
                success = True

        # if none worked, check for active session
        # used in swagger UI
        if not success:
            if login.current_user.is_authenticated:
                g.user = login.current_user
                success = True
        if success:
            return f(*args, **kwargs)
        else:
            _error_abort(401, message)
    return decorated


@jwt_required()
def auth_jwt():
    """
    A helper function that throws JWTError if JWT is not set
    """
    g.user = current_identity


def auth_basic():
    """
    Check for basic auth in header. Return a tuple as result
    The second value of tuple is set only when user tried basic_auth
    """
    auth = request.authorization  # only works in Basic auth
    if not auth:
        return (False, '')
    user = UserModel.query.filter_by(email=auth.username).first()
    auth_ok = False
    if user is not None:
        auth_ok = check_password_hash(
            auth.password.encode('utf-8'),
            user.password.encode('utf-8'),
            user.salt)
    if not auth_ok:
        return (False, 'Authentication failed. Wrong username or password')
    g.user = user
    return (True, '')
