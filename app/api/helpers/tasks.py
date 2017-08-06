import requests
from marrow.mailer import Mailer, Message

from app import celery
from app.api.helpers.utilities import strip_tags

"""
Define all API v2 celery tasks here
This is done to resolve circular imports
"""
import logging
import traceback

from flask import url_for

from app.api.helpers.request_context_task import RequestContextTask
# from errors import BaseError, ServerError
# from export_helpers import send_export_mail
# from app.api.exports import event_export_task_base
from app.settings import get_settings


@celery.task(name='send.email.post')
def send_email_task(payload, headers):
    requests.post(
        "https://api.sendgrid.com/api/mail.send.json",
        data=payload,
        headers=headers
    )


@celery.task(name='send.email.post.smtp')
def send_mail_via_smtp_task(config, payload):
    mailer_config = {
        'transport': {
            'use': 'smtp',
            'host': config['host'],
            'username': config['username'],
            'password': config['password'],
            'tls': config['encryption'],
            'port': config['port']
        }
    }

    mailer = Mailer(mailer_config)
    mailer.start()
    message = Message(author=payload['from'], to=payload['to'])
    message.subject = payload['subject']
    message.plain = strip_tags(payload['html'])
    message.rich = payload['html']
    mailer.send(message)
    mailer.stop()


@celery.task(base=RequestContextTask, name='export.event', bind=True)
def export_event_task(self, event_id, settings):
    try:
        logging.info('Exporting started')
        path = event_export_task_base(event_id, settings)
        # task_id = self.request.id.__str__()  # str(async result)
        if get_settings()['storage_place'] == 'local' or get_settings()['storage_place'] == None:
            download_url = url_for(
                'api.exports_export_download', event_id=event_id, path=path
            )
        else:
            download_url = path

        result = {
            'download_url': download_url
        }
    except Exception as e:
        print(traceback.format_exc())
        result = {'__error': True, 'result': e.to_dict()}
    logging.info('Exporting done.. sending email')
    # send email
    # send_export_mail(event_id, result)
    return result
