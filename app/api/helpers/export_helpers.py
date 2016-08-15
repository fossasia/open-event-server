import json
import os
import shutil
import requests
from collections import OrderedDict
from datetime import datetime
from flask import request, g, url_for
from flask_restplus import marshal

from app.models.export_jobs import ExportJob
from app.models.event import Event as EventModel
from app.helpers.data import save_to_db
from app.helpers.data_getter import DataGetter
from app.helpers.helpers import send_email_after_export

from ..events import DAO as EventDAO, EVENT as EVENT_MODEL
from ..microlocations import DAO as MicrolocationDAO, MICROLOCATION
from ..sessions import DAO as SessionDAO, SESSION, \
    TypeDAO as SessionTypeDAO, SESSION_TYPE
from ..speakers import DAO as SpeakerDAO, SPEAKER
from ..sponsors import DAO as SponsorDAO, SPONSOR
from ..tracks import DAO as TrackDAO, TRACK
from .non_apis import CustomFormDAO, CUSTOM_FORM
from import_helpers import is_downloadable, get_filename_from_cd


# DELETE FIELDS
# All fields to be deleted go here
EVENT = EVENT_MODEL.clone('EventExport')
del EVENT['creator'].model['id']


EXPORTS = [
    ('event', EventDAO, EVENT),
    ('microlocations', MicrolocationDAO, MICROLOCATION),
    ('sessions', SessionDAO, SESSION),
    ('speakers', SpeakerDAO, SPEAKER),
    ('sponsors', SponsorDAO, SPONSOR),
    ('tracks', TrackDAO, TRACK),
    ('session_types', SessionTypeDAO, SESSION_TYPE),
    ('forms', CustomFormDAO, CUSTOM_FORM)
]

# order of keys in export json
FIELD_ORDER = {
    'event': [
        'id', 'name', 'latitude', 'longitude', 'location_name', 'start_time', 'end_time',
        'timezone', 'description', 'background_image', 'logo', 'organizer_name',
        'organizer_description', 'event_url', 'social_links', 'ticket_url', 'privacy', 'type',
        'topic', 'sub_topic', 'code_of_conduct', 'copyright'
    ],
    'microlocations': ['id', 'name', 'floor'],
    'sessions': [
        'id', 'title', 'subtitle', 'short_abstract', 'long_abstract', 'start_time', 'end_time',
        'session_type', 'track', 'comments', 'language', 'slides', 'audio', 'video'
    ],
    'speakers': [
        'id', 'name', 'email', 'mobile', 'photo', 'organisation', 'position', 'country',
        'short_biography', 'long_biography', 'website', 'twitter', 'facebook', 'github', 'linkedin'
    ],
    'sponsors': ['id', 'name', 'logo', 'level', 'sponsor_type', 'url', 'description'],
    'tracks': ['id', 'name', 'color'],
    'session_types': ['id', 'name', 'length'],
    'forms': []
}

# keep sync with storage.UPLOAD_PATHS
DOWNLOAD_FIEDLS = {
    'sessions': {
        'video': ['video', '/videos/session_%d'],
        'audio': ['audio', '/audios/session_%d'],
        'slides': ['document', '/slides/session_%d']
    },
    'speakers': {
        'photo': ['image', '/images/speakers/%s_%d']
    },
    'event': {
        'logo': ['image', '/images/logo'],
        'background_image': ['image', '/images/background']
    },
    'sponsors': {
        'logo': ['image', '/images/sponsors/logo_%d']
    },
    'tracks': {
        'track_image_url': ['image', '/images/tracks/image_%d']
    }
}

# strings to remove in a filename
FILENAME_EXCLUDE = '<>:"/\|?*;'


# FUNCTIONS

def _order_json(data, srv):
    """
    sorts the data a/c FIELD_ORDER and returns.
    If some keys are not included in FIELD_ORDER, they go at last, sorted alphabetically
    """
    new_data = OrderedDict()
    for field in FIELD_ORDER[srv[0]]:
        new_data[field] = data[field]
        data.pop(field, None)
    # remaining fields, sort and add
    # https://docs.python.org/2/library/collections.html#collections.OrderedDict
    data = OrderedDict(sorted(data.items(), key=lambda t: t[0]))
    for key in data:
        new_data[key] = data[key]
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
            path = path % (make_speaker_name(data['name']), data['id'])
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
    d = {}
    d['root_url'] = request.url_root
    return d


def export_event_json(event_id, settings):
    """
    Exports the event as a zip on the server and return its path
    """
    # make directory
    dir_path = 'static/exports/event%d' % event_id
    if os.path.isdir(dir_path):
        shutil.rmtree(dir_path, ignore_errors=True)
    os.mkdir(dir_path)
    # save to directory
    for e in EXPORTS:
        if e[0] == 'event':
            data = _order_json(marshal(e[1].get(event_id), e[2]), e)
            _download_media(data, 'event', dir_path, settings)
        else:
            data = marshal(e[1].list(event_id), e[2])
            for count in range(len(data)):
                data[count] = _order_json(data[count], e)
                _download_media(data[count], e[0], dir_path, settings)
        data_str = json.dumps(data, indent=4)
        fp = open(dir_path + '/' + e[0], 'w')
        fp.write(data_str)
        fp.close()
    # add meta
    data_str = json.dumps(_generate_meta(), sort_keys=True, indent=4)
    fp = open(dir_path + '/meta', 'w')
    fp.write(data_str)
    fp.close()
    # make zip
    shutil.make_archive(dir_path, 'zip', dir_path)
    return os.path.realpath('.') + '/' + dir_path + '.zip'


# HELPERS

def create_export_job(task_id, event_id):
    """
    Create export job for an export that is going to start
    """
    export_job = ExportJob.query.filter_by(event_id=event_id).first()
    task_url = url_for('api.extras_celery_task', task_id=task_id)
    if export_job:
        export_job.task = task_url
        export_job.user_email = g.user.email
        export_job.event = EventModel.query.get(event_id)
        export_job.start_time = datetime.now()
    else:
        export_job = ExportJob(
            task=task_url, user_email=g.user.email,
            event=EventModel.query.get(event_id)
        )
    save_to_db(export_job, 'ExportJob saved')


def send_export_mail(event_id, result):
    """
    send export event mail after the process is complete
    """
    job = DataGetter.get_export_jobs(event_id)
    if not job:  # job not stored, happens in case of CELERY_ALWAYS_EAGER
        return
    event = EventModel.query.get(event_id)
    if not event:
        event_name = '(Undefined)'
    else:
        event_name = event.name
    send_email_after_export(job.user_email, event_name, result)


# FIELD DATA FORMATTERS

def make_speaker_name(name):
    """Make speaker image filename for export"""
    for _ in FILENAME_EXCLUDE:
        name = name.replace(_, ' ')
    return ''.join(s.title() for s in name.split() if s)
