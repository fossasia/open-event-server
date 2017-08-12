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
from app.api.helpers.mail import send_export_mail
from app.api.helpers.db import safe_query
from app.models.event import Event
from app.models import db
from app.api.exports import event_export_task_base
from app.api.imports import import_event_task_base
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
def export_event_task(self, email, event_id, settings):
    event = safe_query(db, Event, 'id', event_id, 'event_id')
    try:
        logging.info('Exporting started')
        path = event_export_task_base(event_id, settings)
        # task_id = self.request.id.__str__()  # str(async result)
        download_url = path

        result = {
            'download_url': download_url
        }
        logging.info('Exporting done.. sending email')
        send_export_mail(email=email, event_name=event.name, download_url=download_url)
    except Exception as e:
        print(traceback.format_exc())
        result = {'__error': True, 'result': str(e)}
        logging.info('Error in exporting.. sending email')
        send_export_mail(email=email, event_name=event.name, error_text=str(e))

    return result


@celery.task(base=RequestContextTask, name='import.event', bind=True)
def import_event_task(self, file, source_type, creator_id):
    """Import Event Task"""
    task_id = self.request.id.__str__()  # str(async result)
    try:
        logging.info('Importing started')
        result = import_event_task_base(self, file, source_type, creator_id)
        logging.info('Importing done..')
    except Exception as e:
        print(traceback.format_exc())
        result = {'__error': True, 'result': str(e)}

    return result
