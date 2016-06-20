import zipfile
import os
import shutil
import json
from flask import request
from errors import NotFoundError
from werkzeug import secure_filename

from open_event.helpers.data import save_to_db
from open_event.models.custom_forms import CustomForms
from ..events import DAO as EventDAO
from ..microlocations import DAO as MicrolocationDAO
from ..sessions import DAO as SessionDAO, TypeDAO as SessionTypeDAO
from ..speakers import DAO as SpeakerDAO
from ..sponsors import DAO as SponsorDAO
from ..tracks import DAO as TrackDAO

from errors import BaseError, ServerError

IMPORT_SERIES = [
    ('microlocations', MicrolocationDAO),
    ('sponsors', SponsorDAO),
    ('speakers', SpeakerDAO),
    ('tracks', TrackDAO),
    ('session_types', SessionTypeDAO),
    ('sessions', SessionDAO)
]

DELETE_FIELDS = {
    'event': ['creator'],
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


def _allowed_file(filename, ext):
    return '.' in filename and filename.rsplit('.', 1)[1] in ext


def get_file_from_request(ext=[], folder='static/temp/', name='file'):
    """
    Get file from a request, save it locally and return its path
    """
    if 'file' not in request.files:
        raise NotFoundError('File not found')
    file = request.files['file']
    if file.filename == '':
        raise NotFoundError('File not found')
    if not _allowed_file(file.filename, ext):
        raise NotFoundError('Invalid file type')
    filename = secure_filename(file.filename)
    path = folder + filename
    file.save(path)
    return path


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
    # sort by id
    data.sort(key=lambda k: k['id'])
    ids = {}
    # start creating
    for obj in data:
        # trim id field
        old_id, obj = _trim_id(obj)
        # delete not needed fields
        obj = _delete_fields(srv, obj)
        # related
        obj = _fix_related_fields(srv, obj, service_ids)
        # create object
        new_obj = srv[1].create(event_id, obj, 'dont')[0]
        ids[old_id] = new_obj.id

    return ids


def import_event_json(zip_path):
    """
    Imports and creates event from json zip
    """
    path = 'static/temp/import_event'
    # delete existing files
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
    # extract files from zip
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall('static/temp/import_event')
    # create event
    data = json.loads(open(path + '/event.json', 'r').read())
    _, data = _trim_id(data)
    data = _delete_fields(('event', EventDAO), data)
    new_event = EventDAO.create(data, 'dont')[0]

    # create other services
    try:
        service_ids = {}
        for item in IMPORT_SERIES:
            data = open(path + '/%s.json' % item[0], 'r').read()
            dic = json.loads(data)
            changed_ids = create_service_from_json(
                dic, item, new_event.id, service_ids)
            service_ids[item[0]] = changed_ids.copy()
    except BaseError as e:
        EventDAO.delete(new_event.id)
        raise e
    except Exception:
        EventDAO.delete(new_event.id)
        raise ServerError()

    custom_form = CustomForms(event_id=new_event.id,
                              session_form='{"title":{"include":1,"require":1},"subtitle":{"include":0,"require":0},'
                                           '"short_abstract":{"include":1,"require":0},"long_abstract":{"include":0,'
                                           '"require":0},"comments":{"include":1,"require":0},"track":{"include":0,'
                                           '"require":0},"session_type":{"include":0,"require":0},"language":{"include":0,'
                                           '"require":0},"slides":{"include":1,"require":0},"video":{"include":0,'
                                           '"require":0},"audio":{"include":0,"require":0}}',
                              speaker_form='{"name":{"include":1,"require":1},"email":{"include":1,"require":1},'
                                           '"photo":{"include":1,"require":0},"organisation":{"include":1,'
                                           '"require":0},"position":{"include":1,"require":0},"country":{"include":1,'
                                           '"require":0},"short_biography":{"include":1,"require":0},"long_biography"'
                                           ':{"include":0,"require":0},"mobile":{"include":0,"require":0},'
                                           '"website":{"include":1,"require":0},"facebook":{"include":0,"require":0},'
                                           '"twitter":{"include":1,"require":0},"github":{"include":0,"require":0},'
                                           '"linkedin":{"include":0,"require":0}}')

    save_to_db(custom_form, "Custom form saved")
    return new_event
