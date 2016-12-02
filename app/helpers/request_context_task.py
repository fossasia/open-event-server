"""
Celery task wrapper to set request context vars and global
vars when a task is executed
Based on http://xion.io/post/code/celery-include-flask-request-context.html
"""
from celery import Task
from flask import has_request_context, request, g

from app import current_app as app

__all__ = ['RequestContextTask']


class RequestContextTask(Task):
    """Base class for tasks that originate from Flask request handlers
    and carry over most of the request context data.
    This has an advantage of being able to access all the usual information
    that the HTTP request has and use them within the task. Pontential
    use cases include e.g. formatting URLs for external use in emails sent
    by tasks.
    """
    abstract = True

    #: Name of the additional parameter passed to tasks
    #: that contains information about the original Flask request context.
    CONTEXT_ARG_NAME = '_flask_request_context'
    GLOBALS_ARG_NAME = '_flask_global_proxy'
    GLOBAL_KEYS = ['user']

    def __call__(self, *args, **kwargs):
        """Execute task code with given arguments."""
        call = lambda: super(RequestContextTask, self).__call__(*args, **kwargs)

        # set context
        context = kwargs.pop(self.CONTEXT_ARG_NAME, None)
        gl = kwargs.pop(self.GLOBALS_ARG_NAME, {})

        if context is None or has_request_context():
            return call()

        with app.test_request_context(**context):
            # set globals
            for i in gl:
                setattr(g, i, gl[i])
            # call
            result = call()
            # process a fake "Response" so that
            # ``@after_request`` hooks are executed
            # app.process_response(make_response(result or ''))

        return result

    def apply_async(self, args=None, kwargs=None, **rest):
        # if rest.pop('with_request_context', True):
        self._include_request_context(kwargs)
        self._include_global(kwargs)
        return super(RequestContextTask, self).apply_async(args, kwargs, **rest)

    def apply(self, args=None, kwargs=None, **rest):
        # if rest.pop('with_request_context', True):
        self._include_request_context(kwargs)
        self._include_global(kwargs)
        return super(RequestContextTask, self).apply(args, kwargs, **rest)

    def retry(self, args=None, kwargs=None, **rest):
        # if rest.pop('with_request_context', True):
        self._include_request_context(kwargs)
        self._include_global(kwargs)
        return super(RequestContextTask, self).retry(args, kwargs, **rest)

    def _include_request_context(self, kwargs):
        """Includes all the information about current Flask request context
        as an additional argument to the task.
        """
        if not has_request_context():
            return

        # keys correspond to arguments of :meth:`Flask.test_request_context`
        context = {
            'path': request.path,
            'base_url': request.url_root,
            'method': request.method,
            'headers': dict(request.headers),
        }
        if '?' in request.url:
            context['query_string'] = request.url[(request.url.find('?') + 1):]

        kwargs[self.CONTEXT_ARG_NAME] = context

    def _include_global(self, kwargs):
        d = {}
        for z in self.GLOBAL_KEYS:
            if hasattr(g, z):
                d[z] = getattr(g, z)
        kwargs[self.GLOBALS_ARG_NAME] = d
