"""
Define all API v2 celery tasks here
This is done to resolve circular imports
"""
from open_event import celery
from open_event.helpers.request_context_task import RequestContextTask
from errors import BaseError

from ..imports import import_event_task_base


@celery.task(base=RequestContextTask, name='import.event', bind=True,
             throws=(BaseError,))
def import_event_task(self, file):
    return import_event_task_base(file)
