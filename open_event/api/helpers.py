from flask.ext.restplus.errors import abort


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


def get_object_or_404(klass, id):
    """Get a specific object of a model class given its identifier. In case
    the object is not found, 404 is returned.
    `klass` can be a model such as a Track, Event, Session, etc.
    """
    queryset = _get_queryset(klass)
    obj = queryset.get(id)
    if obj is None:
        abort(404, '{} does not exist'.format(klass.__name__))
    return obj
