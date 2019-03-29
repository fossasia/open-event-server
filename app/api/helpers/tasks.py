import csv
import json
import os
import requests
import uuid

from flask import current_app, render_template
from marrow.mailer import Mailer, Message

from app import make_celery
from app.api.helpers.utilities import strip_tags
from app.models.session import Session
from app.models.speaker import Speaker

"""
Define all API v2 celery tasks here
This is done to resolve circular imports
"""
import logging
import traceback

from app.api.helpers.files import create_save_image_sizes
from app.api.helpers.request_context_task import RequestContextTask
from app.api.helpers.mail import send_export_mail, send_import_mail
from app.api.helpers.notification import send_notif_after_import, send_notif_after_export
from app.api.helpers.db import safe_query
from .import_helpers import update_import_job
from app.models.user import User
from app.models import db
from app.api.exports import event_export_task_base
from app.api.imports import import_event_task_base
from app.models.event import Event
from app.models.order import Order
from app.models.discount_code import DiscountCode
from app.models.ticket_holder import TicketHolder
from app.api.helpers.ICalExporter import ICalExporter
from app.api.helpers.xcal import XCalExporter
from app.api.helpers.pentabarfxml import PentabarfExporter
from app.api.helpers.storage import UploadedFile, upload, UPLOAD_PATHS
from app.api.helpers.db import save_to_db
from app.api.helpers.files import create_save_pdf
import urllib.error

celery = make_celery()


@celery.task(name='send.email.post')
def send_email_task(payload, headers):
    data = {"personalizations": [{"to": []}]}
    data["personalizations"][0]["to"].append({"email": payload["to"]})
    data["from"] = {"email": payload["from"]}
    data["subject"] = payload["subject"]
    data["content"] = [{"type": "text/html", "value": payload["html"]}]
    logging.info('Sending an email regarding {} on behalf of {}'.format(data["subject"], data["from"]))
    try:
        requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            data=json.dumps(data),
            headers=headers,
            verify=False  # doesn't work with verification in celery context
        )
        logging.info('Email sent successfully')
    except Exception:
        logging.exception('Error occured while sending the email')


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
    logging.info('Message sent via SMTP')
    mailer.stop()


@celery.task(base=RequestContextTask, name='resize.event.images', bind=True)
def resize_event_images_task(self, event_id, original_image_url):
    event = safe_query(db, Event, 'id', event_id, 'event_id')
    try:
        logging.info('Event image resizing tasks started {}'.format(original_image_url))
        uploaded_images = create_save_image_sizes(original_image_url, 'event-image', event.id)
        event.large_image_url = uploaded_images['large_image_url']
        event.thumbnail_image_url = uploaded_images['thumbnail_image_url']
        event.icon_image_url = uploaded_images['icon_image_url']
        save_to_db(event)
        logging.info('Resized images saved successfully for event with id: {}'.format(event_id))
    except (urllib.error.HTTPError, urllib.error.URLError):
        logging.exception('Error encountered while generating resized images for event with id: {}'.format(event_id))


@celery.task(base=RequestContextTask, name='resize.user.images', bind=True)
def resize_user_images_task(self, user_id, original_image_url):
    user = safe_query(db, User, 'id', user_id, 'user_id')
    try:
        logging.info('User image resizing tasks started {}'.format(original_image_url))
        uploaded_images = create_save_image_sizes(original_image_url, 'speaker-image', user.id)
        user.original_image_url = uploaded_images['original_image_url']
        user.avatar_url = uploaded_images['original_image_url']
        user.small_image_url = uploaded_images['thumbnail_image_url']
        user.thumbnail_image_url = uploaded_images['thumbnail_image_url']
        user.icon_image_url = uploaded_images['icon_image_url']
        save_to_db(user)
        logging.info('Resized images saved successfully for user with id: {}'.format(user_id))
    except (urllib.error.HTTPError, urllib.error.URLError):
        logging.exception('Error encountered while generating resized images for user with id: {}'.format(user_id))


@celery.task(base=RequestContextTask, name='resize.speaker.images', bind=True)
def resize_speaker_images_task(self, speaker_id, photo_url):
    speaker = safe_query(db, Speaker, 'id', speaker_id, 'speaker_id')
    try:
        logging.info('Speaker image resizing tasks started for speaker with id {}'.format(speaker_id))
        uploaded_images = create_save_image_sizes(photo_url, 'speaker-image', speaker_id)
        speaker.small_image_url = uploaded_images['small_image_url']
        speaker.thumbnail_image_url = uploaded_images['thumbnail_image_url']
        speaker.icon_image_url = uploaded_images['icon_image_url']
        save_to_db(speaker)
        logging.info('Resized images saved successfully for speaker with id: {}'.format(speaker_id))
    except (urllib.error.HTTPError, urllib.error.URLError):
        logging.exception('Error encountered while generating resized images for event with id: {}'.format(speaker_id))


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
        result = {'__error': True, 'result': str(e)}
        logging.warning('Error in exporting.. sending email')
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
        result = {'__error': True, 'result': str(e)}
        logging.warning('Error in importing the event')
        update_import_job(task_id, str(e), e.status if hasattr(e, 'status') else 'FAILURE')
        send_import_mail(email=email, error_text=str(e))
        send_notif_after_import(user=user, error_text=str(e))

    return result


@celery.task(base=RequestContextTask, name='export.ical', bind=True)
def export_ical_task(self, event_id, temp=True):
    event = safe_query(db, Event, 'id', event_id, 'event_id')

    try:
        if temp:
            filedir = os.path.join(current_app.config.get('BASE_DIR'), 'static/uploads/temp/' + event_id + '/')
        else:
            filedir = os.path.join(current_app.config.get('BASE_DIR'), 'static/uploads/' + event_id + '/')

        if not os.path.isdir(filedir):
            os.makedirs(filedir)
        filename = "ical.ics"
        file_path = os.path.join(filedir, filename)
        with open(file_path, "w") as temp_file:
            temp_file.write(str(ICalExporter.export(event_id), 'utf-8'))
        ical_file = UploadedFile(file_path=file_path, filename=filename)
        if temp:
            ical_url = upload(ical_file, UPLOAD_PATHS['exports-temp']['ical'].format(event_id=event_id))
        else:
            ical_url = upload(ical_file, UPLOAD_PATHS['exports']['ical'].format(event_id=event_id))
        result = {
            'download_url': ical_url
        }
        if not temp:
            event.ical_url = ical_url
            save_to_db(event)

    except Exception as e:
        result = {'__error': True, 'result': str(e)}
        logging.error('Error in ical download')

    return result


@celery.task(base=RequestContextTask, name='export.xcal', bind=True)
def export_xcal_task(self, event_id, temp=True):
    event = safe_query(db, Event, 'id', event_id, 'event_id')

    try:
        if temp:
            filedir = os.path.join(current_app.config.get('BASE_DIR'), 'static/uploads/temp/' + event_id + '/')
        else:
            filedir = os.path.join(current_app.config.get('BASE_DIR'), 'static/uploads/' + event_id + '/')

        if not os.path.isdir(filedir):
            os.makedirs(filedir)
        filename = "xcal.xcs"
        file_path = os.path.join(filedir, filename)
        with open(file_path, "w") as temp_file:
            temp_file.write(str(XCalExporter.export(event_id), 'utf-8'))
        xcal_file = UploadedFile(file_path=file_path, filename=filename)
        if temp:
            xcal_url = upload(xcal_file, UPLOAD_PATHS['exports-temp']['xcal'].format(event_id=event_id))
        else:
            xcal_url = upload(xcal_file, UPLOAD_PATHS['exports']['xcal'].format(event_id=event_id))
        result = {
            'download_url': xcal_url
        }
        if not temp:
            event.xcal_url = xcal_url
            save_to_db(event)

    except Exception as e:
        result = {'__error': True, 'result': str(e)}
        logging.error('Error in xcal download')

    return result


@celery.task(base=RequestContextTask, name='export.pentabarf', bind=True)
def export_pentabarf_task(self, event_id, temp=True):
    event = safe_query(db, Event, 'id', event_id, 'event_id')

    try:
        if temp:
            filedir = os.path.join(current_app.config.get('BASE_DIR'), 'static/uploads/temp/' + event_id + '/')
        else:
            filedir = os.path.join(current_app.config.get('BASE_DIR'), 'static/uploads/' + event_id + '/')

        if not os.path.isdir(filedir):
            os.makedirs(filedir)
        filename = "pentabarf.xml"
        file_path = os.path.join(filedir, filename)
        with open(file_path, "w") as temp_file:
            temp_file.write(str(PentabarfExporter.export(event_id), 'utf-8'))
        pentabarf_file = UploadedFile(file_path=file_path, filename=filename)
        if temp:
            pentabarf_url = upload(pentabarf_file, UPLOAD_PATHS['exports-temp']['pentabarf'].format(event_id=event_id))
        else:
            pentabarf_url = upload(pentabarf_file, UPLOAD_PATHS['exports']['pentabarf'].format(event_id=event_id))
        result = {
            'download_url': pentabarf_url
        }
        if not temp:
            event.pentabarf_url = pentabarf_url
            save_to_db(event)

    except Exception as e:
        result = {'__error': True, 'result': str(e)}
        logging.error('Error in pentabarf download')

    return result


@celery.task(base=RequestContextTask, name='export.order.csv', bind=True)
def export_order_csv_task(self, event_id):
    orders = db.session.query(Order).filter_by(event_id=event_id)

    try:
        filedir = os.path.join(current_app.config.get('BASE_DIR'), 'static/uploads/temp/')
        if not os.path.isdir(filedir):
            os.makedirs(filedir)
        filename = "order-{}.csv".format(uuid.uuid1().hex)
        file_path = os.path.join(filedir, filename)

        with open(file_path, "w") as temp_file:
            writer = csv.writer(temp_file)
            from app.api.helpers.csv_jobs_util import export_orders_csv
            content = export_orders_csv(orders)
            for row in content:
                writer.writerow(row)
        order_csv_file = UploadedFile(file_path=file_path, filename=filename)
        order_csv_url = upload(order_csv_file,
                               UPLOAD_PATHS['exports-temp']['csv'].format(event_id=event_id, identifier=''))
        result = {
            'download_url': order_csv_url
        }
    except Exception as e:
        result = {'__error': True, 'result': str(e)}
        logging.error('Error in exporting as CSV')

    return result


@celery.task(base=RequestContextTask, name='export.order.pdf', bind=True)
def export_order_pdf_task(self, event_id):
    orders = db.session.query(Order).filter_by(event_id=event_id)
    event = db.session.query(Event).filter_by(id=int(event_id)).first()
    discount_code = db.session.query(DiscountCode).filter_by(event_id=event_id)
    try:
        order_pdf_url = create_save_pdf(
            render_template('pdf/orders.html', event=event, event_id=event_id, orders=orders,
                            discount_code=discount_code),
            UPLOAD_PATHS['exports-temp']['pdf'].format(event_id=event_id, identifier=''))
        result = {
            'download_url': order_pdf_url
        }
    except Exception as e:
        result = {'__error': True, 'result': str(e)}
        logging.error('Error in exporting order as pdf')

    return result


@celery.task(base=RequestContextTask, name='export.attendees.csv', bind=True)
def export_attendees_csv_task(self, event_id):
    attendees = db.session.query(TicketHolder).filter_by(event_id=event_id)
    try:
        filedir = os.path.join(current_app.config.get('BASE_DIR'), 'static/uploads/temp/')
        if not os.path.isdir(filedir):
            os.makedirs(filedir)
        filename = "attendees-{}.csv".format(uuid.uuid1().hex)
        file_path = os.path.join(filedir, filename)

        with open(file_path, "w") as temp_file:
            writer = csv.writer(temp_file)
            from app.api.helpers.csv_jobs_util import export_attendees_csv
            content = export_attendees_csv(attendees)
            for row in content:
                writer.writerow(row)
        attendees_csv_file = UploadedFile(file_path=file_path, filename=filename)
        attendees_csv_url = upload(attendees_csv_file,
                                   UPLOAD_PATHS['exports-temp']['csv'].format(event_id=event_id, identifier=''))
        result = {
            'download_url': attendees_csv_url
        }
    except Exception as e:
        result = {'__error': True, 'result': str(e)}
        logging.error('Error in exporting attendees list as CSV')


    return result


@celery.task(base=RequestContextTask, name='export.attendees.pdf', bind=True)
def export_attendees_pdf_task(self, event_id):
    attendees = db.session.query(TicketHolder).filter_by(event_id=event_id)
    try:
        attendees_pdf_url = create_save_pdf(
            render_template('pdf/attendees_pdf.html', holders=attendees),
            UPLOAD_PATHS['exports-temp']['pdf'].format(event_id=event_id, identifier=''))
        result = {
            'download_url': attendees_pdf_url
        }
    except Exception as e:
        result = {'__error': True, 'result': str(e)}
        logging.error('Error in exporting attendees list as PDF')



    return result


@celery.task(base=RequestContextTask, name='export.sessions.csv', bind=True)
def export_sessions_csv_task(self, event_id):
    sessions = db.session.query(Session).filter_by(event_id=event_id)
    try:
        filedir = os.path.join(current_app.config.get('BASE_DIR'), 'static/uploads/temp/')
        if not os.path.isdir(filedir):
            os.makedirs(filedir)
        filename = "sessions-{}.csv".format(uuid.uuid1().hex)
        file_path = os.path.join(filedir, filename)

        with open(file_path, "w") as temp_file:
            writer = csv.writer(temp_file)
            from app.api.helpers.csv_jobs_util import export_sessions_csv
            content = export_sessions_csv(sessions)
            for row in content:
                writer.writerow(row)
        sessions_csv_file = UploadedFile(file_path=file_path, filename=filename)
        sessions_csv_url = upload(sessions_csv_file,
                                  UPLOAD_PATHS['exports-temp']['csv'].format(event_id=event_id, identifier=''))
        result = {
            'download_url': sessions_csv_url
        }
    except Exception as e:
        result = {'__error': True, 'result': str(e)}
        logging.error('Error in exporting sessions as CSV')

    return result


@celery.task(base=RequestContextTask, name='export.speakers.csv', bind=True)
def export_speakers_csv_task(self, event_id):
    speakers = db.session.query(Speaker).filter_by(event_id=event_id)
    try:
        filedir = os.path.join(current_app.config.get('BASE_DIR'), 'static/uploads/temp/')
        if not os.path.isdir(filedir):
            os.makedirs(filedir)
        filename = "speakers-{}.csv".format(uuid.uuid1().hex)
        file_path = os.path.join(filedir, filename)

        with open(file_path, "w") as temp_file:
            writer = csv.writer(temp_file)
            from app.api.helpers.csv_jobs_util import export_speakers_csv
            content = export_speakers_csv(speakers)
            for row in content:
                writer.writerow(row)
        speakers_csv_file = UploadedFile(file_path=file_path, filename=filename)
        speakers_csv_url = upload(speakers_csv_file,
                                  UPLOAD_PATHS['exports-temp']['csv'].format(event_id=event_id, identifier=''))
        result = {
            'download_url': speakers_csv_url
        }
    except Exception as e:
        result = {'__error': True, 'result': str(e)}
        logging.error('Error in exporting speakers list as CSV')

    return result


@celery.task(base=RequestContextTask, name='export.sessions.pdf', bind=True)
def export_sessions_pdf_task(self, event_id):
    sessions = db.session.query(Session).filter_by(event_id=event_id)
    try:
        sessions_pdf_url = create_save_pdf(
            render_template('pdf/sessions_pdf.html', sessions=sessions),
            UPLOAD_PATHS['exports-temp']['pdf'].format(event_id=event_id, identifier=''))
        result = {
            'download_url': sessions_pdf_url
        }
    except Exception as e:
        result = {'__error': True, 'result': str(e)}
        logging.error('Error in exporting sessions as PDF')

    return result


@celery.task(base=RequestContextTask, name='export.speakers.pdf', bind=True)
def export_speakers_pdf_task(self, event_id):
    speakers = db.session.query(Speaker).filter_by(event_id=event_id)
    try:
        speakers_pdf_url = create_save_pdf(
            render_template('pdf/speakers_pdf.html', speakers=speakers),
            UPLOAD_PATHS['exports-temp']['pdf'].format(event_id=event_id, identifier=''))
        result = {
            'download_url': speakers_pdf_url
        }
    except Exception as e:
        result = {'__error': True, 'result': str(e)}
        logging.error('Error in exporting speakers as PDF')

    return result


@celery.task(base=RequestContextTask, name='delete.translations', bind=True)
def delete_translations(self, zip_file_path):
    try:
        os.remove(zip_file_path)
    except:
        logging.exception('Error while deleting translations zip file')
