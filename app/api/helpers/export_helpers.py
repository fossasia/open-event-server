import json
import os
import shutil
import requests
from flask import request, g, url_for
from flask_restplus import marshal

from app.models.export_jobs import ExportJob
from app.models.event import Event as EventModel
from app.helpers.data import save_to_db
from app.helpers.data_getter import DataGetter
from app.helpers.helpers import send_email_after_export

from ..events import DAO as EventDAO, EVENT, \
    LinkDAO as SocialLinkDAO, SOCIAL_LINK
from ..microlocations import DAO as MicrolocationDAO, MICROLOCATION
from ..sessions import DAO as SessionDAO, SESSION, \
    TypeDAO as SessionTypeDAO, SESSION_TYPE
from ..speakers import DAO as SpeakerDAO, SPEAKER
from ..sponsors import DAO as SponsorDAO, SPONSOR
from ..tracks import DAO as TrackDAO, TRACK
from .non_apis import CustomFormDAO, CUSTOM_FORM
from import_helpers import is_downloadable, get_filename_from_cd


EXPORTS = [
    ('event', EventDAO, EVENT),
    ('microlocations', MicrolocationDAO, MICROLOCATION),
    ('sessions', SessionDAO, SESSION),
    ('speakers', SpeakerDAO, SPEAKER),
    ('sponsors', SponsorDAO, SPONSOR),
    ('tracks', TrackDAO, TRACK),
    ('session_types', SessionTypeDAO, SESSION_TYPE),
    ('social_links', SocialLinkDAO, SOCIAL_LINK),
    ('forms', CustomFormDAO, CUSTOM_FORM)
]

# keep sync with storage.UPLOAD_PATHS
DOWNLOAD_FIEDLS = {
    'sessions': {
        'video': ['video', '/videos/session_%d'],
        'audio': ['audio', '/audios/session_%d'],
        'slides': ['document', '/slides/session_%d']
    },
    'speakers': {
        'photo': ['image', '/images/speakers/photo_%d']
    },
    'event': {
        'logo': ['image', '/images/logo'],
        'background_url': ['image', '/images/background']
    },
    'sponsors': {
        'logo': ['image', '/images/sponsors/logo_%d']
    },
    'tracks': {
        'track_image_url': ['image', '/images/tracks/image_%d']
    }
}


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
        if srv != 'event':
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
            data = marshal(e[1].get(event_id), e[2])
            _download_media(data, 'event', dir_path, settings)
        else:
            data = marshal(e[1].list(event_id), e[2])
            for _ in data:
                _download_media(_, e[0], dir_path, settings)
        data_str = json.dumps(data, sort_keys=True, indent=4)
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
