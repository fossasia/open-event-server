"""
Define all API v2 celery tasks here
This is done to resolve circular imports
"""
from open_event import celery
from open_event.helpers.request_context_task import RequestContextTask
from errors import BaseError, ServerError

from ..imports import import_event_task_base


@celery.task(base=RequestContextTask, name='import.event', bind=True,
             throws=(BaseError,))
def import_event_task(self, file):
    try:
        item = import_event_task_base(file)
        return item
    except BaseError as e:
        return {'__error': True, 'result': e.to_dict()}
    except Exception:
        return {'__error': True, 'result': ServerError().to_dict()}
