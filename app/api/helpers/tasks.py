"""
Define all API v2 celery tasks here
This is done to resolve circular imports
"""
import traceback
from flask import url_for

from app import celery
from app.helpers.request_context_task import RequestContextTask
from errors import BaseError, ServerError

from ..imports import import_event_task_base
from ..exports import event_export_task_base


@celery.task(base=RequestContextTask, name='import.event', bind=True,
             throws=(BaseError,))
def import_event_task(self, file):
    try:
        item = import_event_task_base(self, file)
        return item
    except BaseError as e:
        print traceback.format_exc()
        return {'__error': True, 'result': e.to_dict()}
    except Exception:
        print traceback.format_exc()
        return {'__error': True, 'result': ServerError().to_dict()}


@celery.task(base=RequestContextTask, name='export.event', bind=True)
def export_event_task(self, event_id, settings):
    try:
        path = event_export_task_base(event_id, settings)
        # task_id = self.request.id.__str__()  # str(async result)
        return {
            'download_url': url_for(
                'api.exports_export_download', event_id=event_id, path=path
            )
        }
    except BaseError as e:
        return {'__error': True, 'result': e.to_dict()}
    except Exception:
        print traceback.format_exc()
        return {'__error': True, 'result': ServerError().to_dict()}
