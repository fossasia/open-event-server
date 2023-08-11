import json
import os
import shutil
from collections import OrderedDict
from datetime import datetime

import pytz
import requests
from flask import current_app as app
from flask import request, url_for
from flask_jwt_extended import current_user
from flask_login import current_user as current_logged_user

from app.api.helpers.db import save_to_db
from app.api.helpers.storage import UPLOAD_PATHS, UploadedFile, upload
from app.api.helpers.utilities import get_filename_from_cd, is_downloadable
from app.models import db
from app.models.custom_form import CustomForms
from app.models.event import Event
from app.models.export_job import ExportJob
from app.models.microlocation import Microlocation
from app.models.session import Session
from app.models.session_type import SessionType
from app.models.speaker import Speaker
from app.models.sponsor import Sponsor
from app.models.track import Track

# order of keys in export json
FIELD_ORDER = {
    'event': [
        'id',
        'name',
        'latitude',
        'longitude',
        'location_name',
        'starts_at',
        'ends_at',
        'timezone',
        'description',
        'original_image_url',
        'logo_url',
        'owner_name',
        'owner_description',
        'external_event_url',
        'ticket_url',
        'privacy',
        'event_type_id',
        'event_topic_id',
        'event_sub_topic_id',
        'code_of_conduct',
    ],
    'microlocations': ['id', 'name', 'floor'],
    'sessions': [
        'id',
        'title',
        'subtitle',
        'short_abstract',
        'long_abstract',
        'starts_at',
        'ends_at',
        'session_type_id',
        'track_id',
        'comments',
        'language',
        'slides_url',
        'audio_url',
        'video_url',
    ],
    'speakers': [
        'id',
        'name',
        'email',
        'mobile',
        'photo_url',
        'organisation',
        'position',
        'country',
        'short_biography',
        'long_biography',
        'website',
        'twitter',
        'facebook',
        'github',
        'linkedin',
    ],
    'sponsors': ['id', 'name', 'logo_url', 'level', 'type', 'url', 'description'],
    'tracks': ['id', 'name', 'color', 'font_color'],
    'session_types': ['id', 'name', 'length'],
    'forms': [],
}

# keep sync with storage.UPLOAD_PATHS
DOWNLOAD_FIEDLS = {
    'sessions': {
        'video_url': ['video', '/videos/session_%d'],
        'audio_url': ['audio', '/audios/session_%d'],
        'slides_url': ['document', '/slides/session_%d'],
    },
    'speakers': {'photo_url': ['image', '/images/speakers/%s_%d']},
    'event': {
        'logo_url': ['image', '/images/logo'],
        'external_event_url': ['image', '/images/background'],
    },
    'sponsors': {'logo_url': ['image', '/images/sponsors/%s_%d']},
}

DATE_FIELDS = ['starts_at', 'ends_at', 'created_at', 'deleted_at', 'submitted_at']

EXPORTS = [
    ('event', Event),
    ('microlocations', Microlocation),
    ('sessions', Session),
    ('speakers', Speaker),
    ('sponsors', Sponsor),
    ('tracks', Track),
    ('session_types', SessionType),
    ('forms', CustomForms),
]

# strings to remove in a filename
FILENAME_EXCLUDE = r'<>:"/\|?*;'


# FUNCTIONS


def sorted_dict(data):
    """
    sorts a json (dict/list->dict) and returns OrderedDict
    """
    if type(data) is OrderedDict:
        data = dict(data)
    if type(data) is dict:
        data = OrderedDict(sorted(list(data.items()), key=lambda t: t[0]))
    elif type(data) is list:
        for count in range(len(data)):
            data[count] = OrderedDict(
                sorted(list(data[count].items()), key=lambda t: t[0])
            )
    return data


def _order_json(data, srv):
    """
    sorts the data a/c FIELD_ORDER and returns.
    If some keys are not included in FIELD_ORDER, they go at last, sorted alphabetically
    """
    new_data = OrderedDict()
    data.pop('_sa_instance_state', None)
    for field in FIELD_ORDER[srv[0]]:
        if field in DATE_FIELDS and data[field] and type(data[field]) != str:
            new_data[field] = sorted_dict(data[field].isoformat())
        elif field == 'font_color' and 'id' in new_data:
            track = db.session.query(Track).filter(Track.id == new_data['id']).first()
            new_data[field] = track.font_color
        else:
            new_data[field] = sorted_dict(data[field])
        data.pop(field, None)

    # remaining fields, sort and add
    # https://docs.python.org/2/library/collections.html#collections.OrderedDict
    data = OrderedDict(sorted(list(data.items()), key=lambda t: t[0]))
    for key in data:
        if key in DATE_FIELDS and data[key] and type(data[key]) != str:
            new_data[key] = sorted_dict(data[key].isoformat())
        else:
            new_data[key] = sorted_dict(data[key])

    return new_data


def _download_media(data, srv, dir_path, settings):
    """
    Downloads the media and saves it
    """
    if srv not in DOWNLOAD_FIEDLS:
        return
    for i in DOWNLOAD_FIEDLS[srv]:
        if not data[i]:
            continue
        if not settings[DOWNLOAD_FIEDLS[srv][i][0]]:
            continue
        path = DOWNLOAD_FIEDLS[srv][i][1]
        if srv == 'speakers':
            path %= make_filename(data['name']), data['id']
        elif srv == 'sponsors':
            path %= make_filename(data['name']), data['id']
        elif srv != 'event':
            path = path % (data['id'])
        if data[i].find('.') > -1:  # add extension
            ext = data[i].rsplit('.', 1)[1]
            if ext.find('/') == -1:
                path += '.' + ext
        full_path = dir_path + path
        # make dir
        cdir = full_path.rsplit('/', 1)[0]
        if not os.path.isdir(cdir):
            os.makedirs(cdir)
        # download and set
        url = data[i]
        if not is_downloadable(url):
            continue
        try:
            r = requests.get(url, allow_redirects=True)
            ext = get_filename_from_cd(r.headers.get('content-disposition'))[1]
            full_path += ext
            path += ext
            open(full_path, 'wb').write(r.content)
            data[i] = path
        except Exception:
            pass


def _generate_meta():
    """
    Generate Meta information for export
    """
    d = {'root_url': request.url_root}
    return d


def export_event_json(event_id, settings):
    """
    Exports the event as a zip on the server and return its path
    """
    # make directory
    exports_dir = app.config['BASE_DIR'] + '/static/uploads/exports/'
    if not os.path.isdir(exports_dir):
        os.makedirs(exports_dir)
    dir_path = exports_dir + 'event%d' % int(event_id)
    if os.path.isdir(dir_path):
        shutil.rmtree(dir_path, ignore_errors=True)
    os.makedirs(dir_path)
    # save to directory
    for e in EXPORTS:
        if e[0] == 'event':
            query_obj = db.session.query(e[1]).filter(e[1].id == event_id).first()
            data = _order_json(dict(query_obj.__dict__), e)
            _download_media(data, 'event', dir_path, settings)
        else:
            query_objs = db.session.query(e[1]).filter(e[1].event_id == event_id).all()
            data = [_order_json(dict(query_obj.__dict__), e) for query_obj in query_objs]
            for count in range(len(data)):
                data[count] = _order_json(data[count], e)
                _download_media(data[count], e[0], dir_path, settings)
        data_str = json.dumps(
            data, indent=4, ensure_ascii=False, default=handle_unserializable_data
        ).encode('utf-8')
        fp = open(dir_path + '/' + e[0], 'w')
        fp.write(str(data_str, 'utf-8'))
        fp.close()
    # add meta
    data_str = json.dumps(
        _generate_meta(), sort_keys=True, indent=4, ensure_ascii=False
    ).encode('utf-8')
    fp = open(dir_path + '/meta', 'w')
    fp.write(str(data_str, 'utf-8'))
    fp.close()
    # make zip
    shutil.make_archive(dir_path, 'zip', dir_path)
    dir_path = dir_path + ".zip"

    storage_path = UPLOAD_PATHS['exports']['zip'].format(event_id=event_id)
    uploaded_file = UploadedFile(dir_path, dir_path.rsplit('/', 1)[1])
    storage_url = upload(uploaded_file, storage_path)

    return storage_url


def get_current_user():
    if current_user:
        return current_user
    return current_logged_user


# HELPERS


def create_export_job(task_id, event_id):
    """
    Create export job for an export that is going to start
    """
    export_job = ExportJob.query.filter_by(event_id=event_id).first()
    task_url = url_for('tasks.celery_task', task_id=task_id)
    current_logged_user = get_current_user()

    if export_job:

        export_job.task = task_url
        export_job.user_email = current_logged_user.email
        export_job.event = Event.query.get(event_id)
        export_job.starts_at = datetime.now(pytz.utc)
    else:
        export_job = ExportJob(
            task=task_url,
            user_email=current_logged_user.email,
            event=Event.query.get(event_id),
        )
    save_to_db(export_job, 'ExportJob saved')


# FIELD DATA FORMATTERS
def make_filename(name):
    """Make speaker image filename for export"""
    for _ in FILENAME_EXCLUDE:
        name = name.replace(_, ' ')
    return ''.join(s.title() for s in name.split() if s)


def handle_unserializable_data(obj):
    """
    Handles objects which cannot be serialized by json.dumps()
    :param obj: Object to be serialized
    :return: JSON representation of the object
    """
    if isinstance(obj, datetime):
        return obj.__str__()


def create_export_badge_job(task_id, event_id, attendee_id):
    """Create export job for an export that is going to start"""
    export_job = ExportJob.query.filter_by(
        event_id=event_id, attendee_id=attendee_id
    ).first()
    task_url = url_for('tasks.celery_task', task_id=task_id)
    logged_user = get_current_user()

    if export_job:

        export_job.task = task_url
        export_job.user_email = logged_user.email
        export_job.attendee_id = attendee_id
        export_job.event = Event.query.get(event_id)
        export_job.starts_at = datetime.now(pytz.utc)
    else:
        export_job = ExportJob(
            task=task_url,
            user_email=logged_user.email,
            attendee_id=attendee_id,
            event=Event.query.get(event_id),
        )
    save_to_db(export_job, 'ExportJob saved')


def comma_separated_params_to_list(param):
    """
    convert string to list separated by comma
    @param param: string to be separates
    @return: array string
    """
    return list(filter(lambda x: x and x is not None, param.split(',')))
