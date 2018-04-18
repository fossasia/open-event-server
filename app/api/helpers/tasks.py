import requests
from marrow.mailer import Mailer, Message

from app.api.helpers.utilities import strip_tags
from app.views.celery_ import celery

"""
Define all API v2 celery tasks here
This is done to resolve circular imports
"""
import logging
import traceback

from app.api.helpers.request_context_task import RequestContextTask
from app.api.helpers.mail import send_export_mail, send_import_mail
from app.api.helpers.notification import send_notif_after_import, send_notif_after_export
from app.api.helpers.db import safe_query
from .import_helpers import update_import_job
from app.models.event import Event
from app.models.user import User
from app.models import db
from app.api.exports import event_export_task_base
from app.api.imports import import_event_task_base


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
    user = db.session.query(User).filter_by(email=email).first()
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
        send_notif_after_export(user=user, event_name=event.name, download_url=download_url)
    except Exception as e:
        print(traceback.format_exc())
        result = {'__error': True, 'result': str(e)}
        logging.info('Error in exporting.. sending email')
        send_export_mail(email=email, event_name=event.name, error_text=str(e))
        send_notif_after_export(user=user, event_name=event.name, error_text=str(e))

    return result


@celery.task(base=RequestContextTask, name='import.event', bind=True)
def import_event_task(self, email, file, source_type, creator_id):
    """Import Event Task"""
    task_id = self.request.id.__str__()  # str(async result)
    user = db.session.query(User).filter_by(email=email).first()
    try:
        logging.info('Importing started')
        result = import_event_task_base(self, file, source_type, creator_id)
        update_import_job(task_id, result['id'], 'SUCCESS')
        logging.info('Importing done..Sending email')
        send_import_mail(email=email, event_name=result['event_name'], event_url=result['url'])
        send_notif_after_import(user=user, event_name=result[
                                'event_name'], event_url=result['url'])
    except Exception as e:
        print(traceback.format_exc())
        result = {'__error': True, 'result': str(e)}
        update_import_job(task_id, str(e), e.status if hasattr(e, 'status') else 'FAILURE')
        send_import_mail(email=email, error_text=str(e))
        send_notif_after_import(user=user, error_text=str(e))

    return result
