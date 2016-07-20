import zipfile
import os
import shutil
import re
import requests
import traceback
import json
from flask import request
from werkzeug import secure_filename

from flask import current_app as app
from app.helpers.storage import UploadedFile, upload, UploadedMemory, \
    UPLOAD_PATHS
from app.helpers.data import save_to_db
from app.helpers.helpers import update_state

from ..events import DAO as EventDAO, LinkDAO as SocialLinkDAO
from ..microlocations import DAO as MicrolocationDAO
from ..sessions import DAO as SessionDAO, TypeDAO as SessionTypeDAO
from ..speakers import DAO as SpeakerDAO
from ..sponsors import DAO as SponsorDAO
from ..tracks import DAO as TrackDAO
from .non_apis import CustomFormDAO

from errors import BaseError, ServerError, NotFoundError


IMPORT_SERIES = [
    ('social_links', SocialLinkDAO),
    ('microlocations', MicrolocationDAO),
    ('sponsors', SponsorDAO),
    ('speakers', SpeakerDAO),
    ('tracks', TrackDAO),
    ('session_types', SessionTypeDAO),
    ('sessions', SessionDAO),
    ('custom_forms', CustomFormDAO)
]

DELETE_FIELDS = {
    'event': ['creator', 'social_links'],
    'tracks': ['sessions'],
    'speakers': ['sessions']
}

RELATED_FIELDS = {
    'sessions': [
        ('track', 'track_id', 'tracks'),
        ('microlocation', 'microlocation_id', 'microlocations'),
        ('speakers', 'speaker_ids', 'speakers'),
        ('session_type', 'session_type_id', 'session_types')
    ]
}

UPLOAD_QUEUE = []

CUR_ID = None


def _allowed_file(filename, ext):
    return '.' in filename and filename.rsplit('.', 1)[1] in ext


def _available_path(folder, filename):
    """
    takes filename and folder and returns available path
    """
    path = folder + filename
    if not os.path.isfile(path):
        return path
    path += str(1)
    ct = 1
    while os.path.isfile(path):
        ct += 1
        path = folder + filename + str(ct)
    return path


def get_file_from_request(ext=[], folder='/static/temp/', name='file'):
    """
    Get file from a request, save it locally and return its path
    """
    with app.app_context():
        folder = app.config['BASE_DIR'] + folder

    if 'file' not in request.files:
        raise NotFoundError('File not found')
    file = request.files['file']
    if file.filename == '':
        raise NotFoundError('File not found')
    if not _allowed_file(file.filename, ext):
        raise NotFoundError('Invalid file type')
    filename = secure_filename(file.filename)
    path = _available_path(folder, filename)
    file.save(path)
    return path


def make_error(file, er=None, id_=None):
    if er is None:
        er = ServerError()
    istr = 'File %s.json' % file
    if id_ is not None:
        istr = '%s, ID %s' % (istr, id_)
    er.message = '%s, %s' % (istr, er.message)
    return er


def _trim_id(data):
    """
    Trims ID from JSON
    """
    old_id = data['id']
    del data['id']
    return (old_id, data)


def _delete_fields(srv, data):
    """
    Delete not needed fields in POST request
    """
    if srv[0] in DELETE_FIELDS:
        for i in DELETE_FIELDS[srv[0]]:
            if i in data:
                del data[i]
    return data


def _upload_media_queue(srv, obj):
    """
    Add media uploads to queue
    """
    global UPLOAD_QUEUE

    if srv[0] not in UPLOAD_PATHS:
        return
    for i in UPLOAD_PATHS[srv[0]]:
        path = getattr(obj, i)
        if not path:
            continue
        # if not path.startswith('/'):  # relative
        #     continue
        # file OK
        UPLOAD_QUEUE.append({
            'srv': srv,
            'id': obj.id,
            'field': i
        })
    return


def _upload_media(task_handle, event_id, base_path):
    """
    Actually uploads the resources
    """
    global UPLOAD_QUEUE
    total = len(UPLOAD_QUEUE)
    ct = 0

    for i in UPLOAD_QUEUE:
        # update progress
        ct += 1
        update_state(task_handle, 'UPLOADING MEDIA (%d/%d)' % (ct, total))
        # get upload infos
        name, dao = i['srv']
        id_ = i['id']
        if name == 'event':
            item = dao.get(event_id)
        else:
            item = dao.get(event_id, id_)
        # get cur file
        field = i['field']
        path = getattr(item, field)
        if path.startswith('/'):
            # relative files
            path = base_path + path
            if os.path.isfile(path):
                filename = path.rsplit('/', 1)[1]
                file = UploadedFile(path, filename)
            else:
                file = ''  # remove current file setting
        else:
            # absolute links
            try:
                filename = UPLOAD_PATHS[name][field].rsplit('/', 1)[1]
                if is_downloadable(path):
                    r = requests.get(path, allow_redirects=True)
                    file = UploadedMemory(r.content, filename)
                else:
                    file = None
            except:
                file = None
        # don't update current file setting
        if file is None:
            continue
        # upload
        try:
            if file == '':
                raise Exception()
            key = UPLOAD_PATHS[name][field]
            if name == 'event':
                key = key.format(event_id=event_id)
            else:
                key = key.format(event_id=event_id, id=id_)
            print key
            new_url = upload(file, key)
        except Exception:
            print traceback.format_exc()
            new_url = None
        setattr(item, field, new_url)
        save_to_db(item, msg='Url updated')
    # clear queue
    UPLOAD_QUEUE = []
    return


def _fix_related_fields(srv, data, service_ids):
    """
    Fixes the ids services which are related to others.
    Like track, format -> session
    Also fixes their schema
    """
    if srv[0] not in RELATED_FIELDS:
        return data
    for field in RELATED_FIELDS[srv[0]]:
        if field[0] not in data:  # if not present
            data[field[1]] = None
            continue
        # else continue normal
        old_value = data[field[0]]
        if type(old_value) == list:
            ls = []
            for i in old_value:
                old_id = i['id']
                new_id = service_ids[field[2]][old_id]
                ls += [new_id]
            del data[field[0]]
            data[field[1]] = ls
        else:
            if type(old_value) == dict:
                old_id = old_value['id']
            else:
                old_id = old_value
            del data[field[0]]
            if old_id is None:
                data[field[1]] = None
            else:
                data[field[1]] = service_ids[field[2]][old_id]

    return data


def create_service_from_json(data, srv, event_id, service_ids={}):
    """
    Given :data as json, create the service on server
    :service_ids are the mapping of ids of already created services.
        Used for mapping old ids to new
    """
    global CUR_ID
    # sort by id
    data.sort(key=lambda k: k['id'])
    ids = {}
    # start creating
    for obj in data:
        # trim id field
        old_id, obj = _trim_id(obj)
        CUR_ID = old_id
        # delete not needed fields
        obj = _delete_fields(srv, obj)
        # related
        obj = _fix_related_fields(srv, obj, service_ids)
        # create object
        new_obj = srv[1].create(event_id, obj, 'dont')[0]
        ids[old_id] = new_obj.id
        # add uploads to queue
        _upload_media_queue(srv, new_obj)

    return ids


def import_event_json(task_handle, zip_path):
    """
    Imports and creates event from json zip
    """
    global CUR_ID, UPLOAD_QUEUE
    UPLOAD_QUEUE = []
    update_state(task_handle, 'IMPORTING')

    with app.app_context():
        path = app.config['BASE_DIR'] + '/static/temp/import_event'
    # delete existing files
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
    # extract files from zip
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(path)
    # create event
    try:
        data = json.loads(open(path + '/event.json', 'r').read())
        _, data = _trim_id(data)
        srv = ('event', EventDAO)
        data = _delete_fields(srv, data)
        new_event = EventDAO.create(data, 'dont')[0]
        _upload_media_queue(srv, new_event)
    except BaseError as e:
        raise make_error('event', er=e)
    except Exception:
        raise make_error('event')
    # create other services
    try:
        service_ids = {}
        for item in IMPORT_SERIES:
            data = open(path + '/%s.json' % item[0], 'r').read()
            dic = json.loads(data)
            changed_ids = create_service_from_json(
                dic, item, new_event.id, service_ids)
            service_ids[item[0]] = changed_ids.copy()
            CUR_ID = None
    except BaseError as e:
        EventDAO.delete(new_event.id)
        raise make_error(item[0], er=e, id_=CUR_ID)
    except IOError:
        EventDAO.delete(new_event.id)
        raise NotFoundError('File %s.json missing in event zip' % item[0])
    except ValueError:
        EventDAO.delete(new_event.id)
        raise make_error(item[0], er=ServerError('Invalid json'))
    except Exception:
        EventDAO.delete(new_event.id)
        raise make_error(item[0], id_=CUR_ID)
    # run uploads
    _upload_media(task_handle, new_event.id, path)
    # return
    return new_event


##########
# HELPERS
##########

def is_downloadable(url):
    """
    Does the url contain a downloadable resource
    """
    h = requests.head(url, allow_redirects=True)
    header = h.headers
    content_type = header.get('content-type')
    # content_length = header.get('content-length', 1e10)
    if 'text' in content_type.lower():
        return False
    if 'html' in content_type.lower():
        return False
    return True


def get_filename_from_cd(cd):
    """
    Get filename and ext from content-disposition
    """
    if not cd:
        return '', ''
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return '', ''
    fn = fname[0].rsplit('.', 1)
    return fn[0], '' if len(fn) == 1 else ('.' + fn[1])
