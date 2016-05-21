from flask.ext.restplus.errors import abort


def _get_queryset(klass):
    """Returns the queryset for `klass` model"""
    return klass.query


def get_object_list(klass):
    """Get a list of all the objects of a model class. `klass` can be a model
    such as a Track, Event, Session, etc.
    """
    queryset = _get_queryset(klass)
    return queryset.all()


def get_object_or_404(klass, id):
    """Get a specific object of a model class given its identifier. `klass`
    can be a model such as a Track, Event, Session, etc.
    """
    queryset = _get_queryset(klass)
    obj = queryset.get(id)
    if obj is None:
        abort(404, '{} does not exist'.format(klass.__name__))
    return obj
