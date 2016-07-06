import json
from datetime import datetime
from sqlalchemy import func
from functools import wraps, update_wrapper
from flask import request, g, make_response
from flask.ext.restplus import fields
from flask.ext import login
from flask.ext.scrypt import check_password_hash
from flask_jwt import jwt_required, JWTError, current_identity

from open_event.models.event import Event as EventModel
from open_event.models import db
from custom_fields import CustomField
from .errors import NotFoundError, InvalidServiceError, ValidationError, \
    NotAuthorizedError
from open_event.models.user import User as UserModel
from open_event.helpers.data import save_to_db, update_version, delete_from_db

from query_filters import extract_special_queries, apply_special_queries


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
    if hasattr(klass, 'in_trash'):
        queryset = queryset.filter(klass.in_trash != True)
    kwargs, specials = extract_special_queries(kwargs)
    # case insenstive filter
    for i in kwargs:
        if type(kwargs[i]) == str:
            queryset = queryset.filter(
                func.lower(getattr(klass, i)) == kwargs[i].lower())
        else:
            queryset = queryset.filter(getattr(klass, i) == kwargs[i])
    # special filters
    obj_list = apply_special_queries(queryset, specials)
    # return as list
    return list(obj_list)


def get_list_or_404(klass, **kwargs):
    """Abstraction over `get_object_list`.
    Raises 404 error if the `obj_list` is empty.
    """
    obj_list = get_object_list(klass, **kwargs)
    if not obj_list:
        raise NotFoundError(message='Object list is empty')
    return obj_list


def get_object_or_404(klass, id_):
    """Returns a specific object of a model class given its identifier. In case
    the object is not found, 404 is returned.
    `klass` can be a model such as a Track, Event, Session, etc.
    """
    queryset = _get_queryset(klass)
    obj = queryset.get(id_)
    if obj is None or (hasattr(klass, 'in_trash') and obj.in_trash):
        raise NotFoundError(message='{} does not exist'.format(klass.__name__))
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
        raise InvalidServiceError(
            message='{} does not belong to event'.format(klass.__name__))

    return obj


def get_paginated_list(klass, url=None, args={}, **kwargs):
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
    # auto-get url
    if url is None:
        url = request.base_url
    # get page bounds
    start = args['start']
    limit = args['limit']
    # check if page exists
    results = get_object_list(klass, **kwargs)
    count = len(results)
    if (count < start):
        raise NotFoundError(
            message='Start position \'{}\' out of bound'.format(start))
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


def handle_extra_payload(payload, api_model):
    """
    Handles extra keys in payload
    """
    # not checking list type bcoz no such API
    if type(payload) != dict:
        return payload
    data = payload.copy()
    for key in payload:
        if key not in api_model:
            del data[key]
        elif isinstance(api_model[key], fields.Nested):
            data[key] = handle_extra_payload(data[key], api_model[key].model)
        elif isinstance(api_model[key], fields.List):
            temp = []
            for _ in payload[key]:
                temp.append(handle_extra_payload(_, api_model[key].container))
            data[key] = temp
    return data


def validate_payload(payload, api_model):
    """
    Validate payload against an api_model. Aborts in case of failure
    - This function is for custom fields as they can't be validated by
      flask restplus automatically.
    - This is to be called at the start of a post or put method
    """
    # check if any reqd fields are missing in payload
    for key in api_model:
        if api_model[key].required and key not in payload:
            raise ValidationError(
                field=key,
                message='Required field \'{}\' missing'.format(key))
    # check payload
    for key in payload:
        field = api_model[key]
        if isinstance(field, fields.List):
            field = field.container
            data = payload[key]
        elif isinstance(field, fields.Nested):
            if payload[key]:  # not null
                validate_payload(payload[key], field.model)
        else:
            data = [payload[key]]
        if isinstance(field, CustomField) and hasattr(field, 'validate'):
            field.payload = payload
            for i in data:
                if not field.validate(i):
                    raise ValidationError(field=key,
                                          message=field.validation_error %
                                          ('\'%s\'' % key))


def save_db_model(new_model, model_name, event_id=None):
    """
    Save a new/modified model to database
    """
    save_to_db(new_model, "Model %s saved" % model_name)
    if not event_id:
        update_version(event_id, False, "session_ver")
    return new_model


def create_model(model, data, event_id=None):
    """
    Creates a model.
    If event_id is set, the model is assumed as a child of event
    i.e. Service Model
    """
    if event_id is not None:
        get_object_or_404(EventModel, event_id)
        data['event_id'] = event_id
    new_model = model(**data)
    save_to_db(new_model, "Model %s saved" % model.__name__)
    if event_id:
        update_version(event_id, False, "session_ver")
    return new_model


def delete_model(model, item_id, event_id=None):
    """
    Deletes a model
    If event_id is set, it is assumed to be a service model
    """
    if event_id is not None:
        item = get_object_in_event(model, item_id, event_id)
    else:
        item = get_object_or_404(model, item_id)
    if hasattr(item, 'in_trash'):
        item.in_trash = True
        save_to_db(item, '{} moved to trash'.format(model.__name__))
    else:
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
                raise NotAuthorizedError(message=e.error + ': ' + e.description)

        # Basic Auth
        if not success:
            results = auth_basic()
            if not results[0]:
                if results[1]:  # basic auth was set but..
                    raise NotAuthorizedError(message=results[1])
            else:
                success = True

        # if none worked, check for active session
        # used in swagger UI
        if not success:
            if login.current_user.is_authenticated:
                g.user = login.current_user
                success = True
        else:
            g.user.update_lat()
        if success:
            return f(*args, **kwargs)
        else:
            raise NotAuthorizedError(message=message)
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


# Disable caching in a view
# Used in download views
# http://arusahni.net/blog/2014/03/flask-nocache.html
def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
    return update_wrapper(no_cache, view)


def parse_args(parser, keep_none=False):
    """
    Abstraction over flask_restplus.reqparse.parser.parse_args
    It returned None value if a value was not set
    This completely removes that value from the returned dict
    """
    args = parser.parse_args()
    if not keep_none:
        args = {k: v for k, v in args.items() if v is not None}
    return args


def model_custom_form(cf_data, model):
    """
    Sets required setting in a model a/c Custom Form
    """
    tmp = model.clone('TempModel')
    cf = json.loads(cf_data)
    for key in tmp:
        if key in cf and cf[key]['require'] == 1:
            tmp[key].required = True
    return tmp
