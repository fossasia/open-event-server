from flask.ext.restplus.errors import abort

from open_event.models.event import Event as EventModel


def _get_queryset(klass):
    """Returns the queryset for `klass` model"""
    return klass.query


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
        abort(404)
    return obj_list


def get_object_or_404(klass, id_):
    """Returns a specific object of a model class given its identifier. In case
    the object is not found, 404 is returned.
    `klass` can be a model such as a Track, Event, Session, etc.
    """
    queryset = _get_queryset(klass)
    obj = queryset.get(id_)
    if obj is None:
        abort(404, '{} does not exist'.format(klass.__name__))
    return obj


def get_object_in_event(klass, id_, event_id):
    """Returns a object (such as a Session, Track, Speaker, etc.) belonging
    to an Event.

    First checks if Event with `event_id` exists and model `klass` (e.g. Track)
    with `id_` exists.
    If both exist, it checks if model belongs to that Event. If it doesn't,
    it returns a 400 (Bad Request) status.
    """
    event = get_object_or_404(EventModel, event_id)
    obj = get_object_or_404(klass, id_)

    if obj.event_id != event.id:
        abort(400, 'Requested object does not belong to the event')

    return obj
