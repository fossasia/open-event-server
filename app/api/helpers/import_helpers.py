import json
import os
import shutil
import traceback
import uuid
import zipfile

import requests
from flask import current_app as app
from flask import request
from flask_jwt_extended import current_user
from werkzeug.utils import secure_filename

from app.api.helpers.db import save_to_db
from app.api.helpers.errors import NotFoundError, ServerError
from app.api.helpers.storage import UPLOAD_PATHS, UploadedFile, UploadedMemory, upload
from app.api.helpers.utilities import is_downloadable, update_state, write_file
from app.models import db
from app.models.custom_form import CustomForms
from app.models.event import Event
from app.models.import_job import ImportJob
from app.models.microlocation import Microlocation
from app.models.role import Role
from app.models.session import Session
from app.models.session_type import SessionType
from app.models.social_link import SocialLink
from app.models.speaker import Speaker
from app.models.sponsor import Sponsor
from app.models.track import Track
from app.models.user import User
from app.models.users_events_role import UsersEventsRoles

IMPORT_SERIES = [
    ('social_links', SocialLink),
    ('forms', CustomForms),
    ('microlocations', Microlocation),
    ('sponsors', Sponsor),
    ('speakers', Speaker),
    ('tracks', Track),
    ('session_types', SessionType),
    ('sessions', Session),
]

DELETE_FIELDS = {
    'event': ['creator', 'created_at'],
    'tracks': ['sessions', 'font_color'],
    'speakers': ['sessions'],
}

RELATED_FIELDS = {
    'sessions': [
        ('track', 'track_id', 'tracks'),
        ('microlocation', 'microlocation_id', 'microlocations'),
        ('session_type', 'session_type_id', 'session_types'),
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


def get_file_from_request(ext=None, folder=None, name='file'):
    """
    Get file from a request, save it locally and return its path
    """
    if ext is None:
        ext = []

    print("get_file_from_request() INVOKED. We have: request.files = %r" % request.files)

    if name not in request.files:
        raise NotFoundError(source='{}', detail='File not found')
    uploaded_file = request.files[name]
    if uploaded_file.filename == '':
        raise NotFoundError(source='{}', detail='File not found')
    if not _allowed_file(uploaded_file.filename, ext):
        raise NotFoundError(source='{}', detail='Invalid file type')

    if not folder:
        if 'UPLOAD_FOLDER' in app.config:
            folder = app.config['UPLOAD_FOLDER']
        else:
            folder = 'static/uploads/' + UPLOAD_PATHS['temp']['event'].format(
                uuid=uuid.uuid4()
            )
    else:
        with app.app_context():
            folder = app.config['BASE_DIR'] + folder
    if not os.path.isdir(folder):
        os.makedirs(folder)

    filename = secure_filename(uploaded_file.filename)
    uploaded_file.save(os.path.join(folder, filename))
    return os.path.join(folder, filename)


def make_error(uploaded_file, er=None, id_=None):
    if er is None:
        er = ServerError(source='{}', detail="Internal Server Error")
    istr = 'File %s' % uploaded_file
    if id_ is not None:
        istr = f'{istr}, ID {id_}'
    if hasattr(er, 'title'):
        er.title = f'{istr}, {er.title}'
    if not hasattr(er, 'status') or not er.status:
        er.status = 500
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


def create_import_job(task):
    """create import record in db"""
    ij = ImportJob(task=task, user=current_user)
    save_to_db(ij, 'Import job saved')


def update_import_job(task, result, result_status):
    """update import job status"""
    ij = ImportJob.query.filter_by(task=task).first()
    if not ij:
        return
    ij.result = result
    ij.result_status = result_status
    save_to_db(ij, 'Import job updated')


def _upload_media_queue(srv, obj):
    """
    Add media uploads to queue
    """
    global UPLOAD_QUEUE

    if srv[0] not in UPLOAD_PATHS:
        return
    for i in UPLOAD_PATHS[srv[0]]:
        if i in ['original', 'large', 'thumbnail', 'small', 'icon']:
            upload_path = f'{i}_image_url'
        else:
            upload_path = f'{i}_url'
        path = getattr(obj, upload_path)
        if not path:
            continue
        # if not path.startswith('/'):  # relative
        #     continue
        # file OK
        UPLOAD_QUEUE.append({'srv': srv, 'id': obj.id, 'field': i})
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
        update_state(task_handle, 'Uploading media (%d/%d)' % (ct, total))
        # get upload infos
        name, model = i['srv']
        id_ = i['id']
        if name == 'event':
            item = db.session.query(model).filter_by(id=event_id).first()
        else:
            item = (
                db.session.query(model)
                .filter_by(event_id=event_id)
                .filter_by(id=id_)
                .first()
            )
        # get cur file
        if i['field'] in ['original', 'large', 'thumbnail', 'small', 'icon']:
            field = '{}_image_url'.format(i['field'])
        else:
            field = '{}_url'.format(i['field'])
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
            print(key)
            new_url = upload(file, key)
        except Exception:
            print(traceback.format_exc())
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
        if type(old_value) is list:
            ls = []
            for i in old_value:
                old_id = i['id']
                new_id = service_ids[field[2]][old_id]
                ls += [new_id]
            del data[field[0]]
            data[field[1]] = ls
        else:
            if type(old_value) is dict:
                old_id = old_value['id']
            else:
                old_id = old_value
            del data[field[0]]
            if old_id is None:
                data[field[1]] = None
            else:
                data[field[1]] = service_ids[field[2]][old_id]

    return data


def create_service_from_json(task_handle, data, srv, event_id, service_ids=None):
    """
    Given :data as json, create the service on server
    :service_ids are the mapping of ids of already created services.
        Used for mapping old ids to new
    """
    if service_ids is None:
        service_ids = {}
    global CUR_ID
    # sort by id
    data.sort(key=lambda k: k['id'])
    ids = {}
    ct = 0
    total = len(data)
    # start creating
    for obj in data:
        # update status
        ct += 1
        update_state(task_handle, 'Importing %s (%d/%d)' % (srv[0], ct, total))
        # trim id field
        old_id, obj = _trim_id(obj)
        CUR_ID = old_id
        # delete not needed fields
        obj = _delete_fields(srv, obj)
        # related
        obj = _fix_related_fields(srv, obj, service_ids)
        obj['event_id'] = event_id
        # create object
        new_obj = srv[1](**obj)
        save_to_db(new_obj)
        ids[old_id] = new_obj.id
        # add uploads to queue
        _upload_media_queue(srv, new_obj)

    return ids


def import_event_json(task_handle, zip_path, creator_id):
    """
    Imports and creates event from json zip
    """
    global CUR_ID, UPLOAD_QUEUE
    UPLOAD_QUEUE = []
    update_state(task_handle, 'Started')

    with app.app_context():
        path = app.config['BASE_DIR'] + '/static/uploads/import_event'
    # delete existing files
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
    # extract files from zip
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(path)
    # create event
    try:
        update_state(task_handle, 'Importing event core')
        data = json.loads(open(path + '/event').read())
        _, data = _trim_id(data)
        srv = ('event', Event)
        data = _delete_fields(srv, data)
        new_event = Event(**data)
        save_to_db(new_event)
        role = Role.query.filter_by(name=Role.OWNER).first()
        user = User.query.filter_by(id=creator_id).first()
        uer = UsersEventsRoles(user_id=user.id, event_id=new_event.id, role_id=role.id)
        save_to_db(uer, 'Event Saved')
        write_file(
            path + '/social_links',
            json.dumps(data.get('social_links', [])).encode('utf-8'),
        )  # save social_links
        _upload_media_queue(srv, new_event)
    except Exception as e:
        raise make_error('event', er=e)
    # create other services
    item = []  # TODO: Remove workaround for pytype
    try:
        service_ids = {}
        for item in IMPORT_SERIES:
            item[1].is_importing = True
            data = open(path + '/%s' % item[0]).read()
            dic = json.loads(data)
            changed_ids = create_service_from_json(
                task_handle, dic, item, new_event.id, service_ids
            )
            service_ids[item[0]] = changed_ids.copy()
            CUR_ID = None
            item[1].is_importing = False
    except OSError:
        db.session.delete(new_event)
        db.session.commit()
        raise NotFoundError('file', 'File %s missing in event zip' % item[0])
    except ValueError:
        db.session.delete(new_event)
        db.session.commit()
        raise make_error(
            item[0], er=ServerError(source='Zip Upload', detail='Invalid json')
        )
    except Exception:
        print(traceback.format_exc())
        db.session.delete(new_event)
        db.session.commit()
        raise make_error(item[0], id_=CUR_ID)
    # run uploads
    _upload_media(task_handle, new_event.id, path)
    # return
    return new_event
