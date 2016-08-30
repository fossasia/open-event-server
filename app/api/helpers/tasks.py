"""
Define all API v2 celery tasks here
This is done to resolve circular imports
"""
import traceback
import logging
from flask import url_for

from app import celery
from app.helpers.request_context_task import RequestContextTask
from errors import BaseError, ServerError
from export_helpers import send_export_mail
from import_helpers import update_import_job, send_import_mail

from ..imports import import_event_task_base
from ..exports import event_export_task_base


@celery.task(base=RequestContextTask, name='import.event', bind=True,
             throws=(BaseError,))
def import_event_task(self, file):
    """Import Event Task"""
    task_id = self.request.id.__str__()  # str(async result)
    try:
        result = import_event_task_base(self, file)
        update_import_job(task_id, result['id'], 'SUCCESS')
        # return item
    except BaseError as e:
        print traceback.format_exc()
        update_import_job(task_id, e.message, e.status)
        result = {'__error': True, 'result': e.to_dict()}
    except Exception as e:
        print traceback.format_exc()
        update_import_job(task_id, e.message, e.status)
        result = {'__error': True, 'result': ServerError().to_dict()}
    # send email
    send_import_mail(task_id, result)
    # return result
    return result


@celery.task(base=RequestContextTask, name='export.event', bind=True)
def export_event_task(self, event_id, settings):
    try:
        logging.info('Exporting started')
        path = event_export_task_base(event_id, settings)
        # task_id = self.request.id.__str__()  # str(async result)
        result = {
            'download_url': url_for(
                'api.exports_export_download', event_id=event_id, path=path
            )
        }
    except BaseError as e:
        result = {'__error': True, 'result': e.to_dict()}
    except Exception:
        print traceback.format_exc()
        result = {'__error': True, 'result': ServerError().to_dict()}
    logging.info('Exporting done.. sending email')
    # send email
    send_export_mail(event_id, result)
    # return result
    return result
