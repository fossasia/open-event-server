import os
from base64 import b64encode
from shutil import copyfile, rmtree

import boto
import magic
from boto.gs.connection import GSConnection
from boto.s3.connection import S3Connection, OrdinaryCallingFormat
from boto.s3.key import Key
from flask import current_app as app, request
from flask_scrypt import generate_password_hash
from urllib.parse import urlparse
from werkzeug.utils import secure_filename

from app.settings import get_settings

SCHEMES = {80: 'http', 443: 'https'}

#################
# STORAGE SCHEMA
#################

UPLOAD_PATHS = {
    'sessions': {
        'video': 'events/{event_id}/sessions/{id}/video',
        'audio': 'events/{event_id}/audios/{id}/audio',
        'slides': 'events/{event_id}/slides/{id}/slides'
    },
    'speakers': {
        'photo': 'events/{event_id}/speakers/{id}/photo',
        'thumbnail': 'events/{event_id}/speakers/{id}/thumbnail',
        'small': 'events/{event_id}/speakers/{id}/small',
        'icon': 'events/{event_id}/speakers/{id}/icon'
    },
    'event': {
        'logo': 'events/{event_id}/logo',
        'original': 'events/{identifier}/original',
        'thumbnail': 'events/{identifier}/thumbnail',
        'large': 'events/{identifier}/large',
        'icon': 'events/{identifier}/icon'
    },
    'sponsors': {
        'logo': 'events/{event_id}/sponsors/{id}/logo'
    },
    'user': {
        'avatar': 'users/{user_id}/avatar',
        'thumbnail': 'users/{identifier}/thumbnail',
        'original': 'users/{identifier}/original',
        'small': 'users/{identifier}/small',
        'icon': 'users/{identifier}/icon'
    },
    'temp': {
        'event': 'events/temp/{uuid}',
        'image': 'temp/images/{uuid}'
    },
    'exports': {
        'zip': 'exports/{event_id}/zip',
        'pentabarf': 'exports/{event_id}/pentabarf',
        'ical': 'exports/{event_id}/ical',
        'xcal': 'exports/{event_id}/xcal',
        'csv': 'exports/{event_id}/csv/{identifier}',
        'pdf': 'exports/{event_id}/pdf/{identifier}'
    },
    'exports-temp': {
        'zip': 'exports/{event_id}/temp/zip',
        'pentabarf': 'exports/{event_id}/temp/pentabarf',
        'ical': 'exports/{event_id}/temp/ical',
        'xcal': 'exports/{event_id}/temp/xcal',
        'csv': 'exports/{event_id}/csv/{identifier}',
        'pdf': 'exports/{event_id}/pdf/{identifier}'
    },
    'custom-placeholders': {
        'original': 'custom-placeholders/{identifier}/original',
        'thumbnail': 'custom-placeholders/{identifier}/thumbnail',
        'large': 'custom-placeholders/{identifier}/large',
        'icon': 'custom-placeholders/{identifier}/icon'
    },
    'event_topic': {
        'system_image': 'event_topic/{event_topic_id}/system_image'
    },
    'pdf': {
        'ticket_attendee': 'attendees/tickets/pdf/{identifier}'
    }
}


################
# HELPER CLASSES
################

class UploadedFile(object):
    """
    Helper for a disk-file to replicate request.files[ITEM] class
    """

    def __init__(self, file_path, filename):
        self.file_path = file_path
        self.filename = filename
        self.file = open(file_path)

    def save(self, new_path):
        copyfile(self.file_path, new_path)

    def read(self):
        return self.file.read()

    def __exit__(self, *args, **kwargs):
        self.file.close()


class UploadedMemory(object):
    """
    Helper for a memory file to replicate request.files[ITEM] class
    """

    def __init__(self, data, filename):
        self.data = data
        self.filename = filename

    def read(self):
        return self.data

    def save(self, path):
        f = open(path, 'w')
        f.write(str(self.data, 'utf-8'))
        f.close()


#########
# MAIN
#########

def upload(uploaded_file, key, **kwargs):
    """
    Upload handler
    """
    # refresh settings
    aws_bucket_name = get_settings()['aws_bucket_name']
    aws_key = get_settings()['aws_key']
    aws_secret = get_settings()['aws_secret']
    aws_region = get_settings()['aws_region']

    gs_bucket_name = get_settings()['gs_bucket_name']
    gs_key = get_settings()['gs_key']
    gs_secret = get_settings()['gs_secret']

    storage_place = get_settings()['storage_place']

    # upload
    if aws_bucket_name and aws_key and aws_secret and storage_place == 's3':
        return upload_to_aws(aws_bucket_name, aws_region, aws_key, aws_secret, uploaded_file, key, **kwargs)
    elif gs_bucket_name and gs_key and gs_secret and storage_place == 'gs':
        return upload_to_gs(gs_bucket_name, gs_key, gs_secret, uploaded_file, key, **kwargs)
    else:
        return upload_local(uploaded_file, key, **kwargs)


def upload_local(uploaded_file, key, **kwargs):
    """
    Uploads file locally. Base dir - static/media/
    """
    filename = secure_filename(uploaded_file.filename)
    file_relative_path = 'static/media/' + key + '/' + generate_hash(key) + '/' + filename
    file_path = app.config['BASE_DIR'] + '/' + file_relative_path
    dir_path = file_path.rsplit('/', 1)[0]
    # delete current
    try:
        rmtree(dir_path)
    except OSError:
        pass
    # create dirs
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    uploaded_file.save(file_path)
    file_relative_path = '/' + file_relative_path
    if get_settings()['static_domain']:
        return get_settings()['static_domain'] + \
               file_relative_path.replace('/static', '')

    return create_url(request.url, file_relative_path)


def create_url(request_url, file_relative_path):
    """Generates the URL of an uploaded file."""
    url = urlparse(request_url)

    # No need to specify scheme-corresponding port
    port = url.port
    if port and url.scheme == SCHEMES.get(url.port, None):
        port = None

    return '{scheme}://{hostname}:{port}{file_relative_path}'.format(
        scheme=url.scheme, hostname=url.hostname, port=port,
        file_relative_path=file_relative_path).replace(':None', '')


def upload_to_aws(bucket_name, aws_region, aws_key, aws_secret, file, key, acl='public-read'):
    """
    Uploads to AWS at key
    http://{bucket}.s3.amazonaws.com/{key}
    """

    if '.' in bucket_name and aws_region and aws_region != '':
        conn = boto.s3.connect_to_region(
            aws_region,
            aws_access_key_id=aws_key,
            aws_secret_access_key=aws_secret,
            calling_format=OrdinaryCallingFormat()
        )
    else:
        conn = S3Connection(aws_key, aws_secret)

    bucket = conn.get_bucket(bucket_name)
    k = Key(bucket)
    # generate key
    filename = secure_filename(file.filename)
    key_dir = key + '/' + generate_hash(key) + '/'
    k.key = key_dir + filename
    # delete old data
    for item in bucket.list(prefix='/' + key_dir):
        item.delete()
    # set object settings

    file_data = file.read()
    file_mime = magic.from_buffer(file_data, mime=True)
    size = len(file_data)
    sent = k.set_contents_from_string(
        file_data,
        headers={
            'Content-Disposition': 'attachment; filename=%s' % filename,
            'Content-Type': '%s' % file_mime
        }
    )
    k.set_acl(acl)
    s3_url = 'https://%s.s3.amazonaws.com/' % bucket_name
    if sent == size:
        return s3_url + k.key
    return False


def upload_to_gs(bucket_name, client_id, client_secret, file, key, acl='public-read'):
    conn = GSConnection(client_id, client_secret, calling_format=OrdinaryCallingFormat())
    bucket = conn.get_bucket(bucket_name)
    k = Key(bucket)
    # generate key
    filename = secure_filename(file.filename)
    key_dir = key + '/' + generate_hash(key) + '/'
    k.key = key_dir + filename
    # delete old data
    for item in bucket.list(prefix='/' + key_dir):
        item.delete()
    # set object settings

    file_data = file.read()
    file_mime = magic.from_buffer(file_data, mime=True)
    size = len(file_data)
    sent = k.set_contents_from_string(
        file_data,
        headers={
            'Content-Disposition': 'attachment; filename=%s' % filename,
            'Content-Type': '%s' % file_mime
        }
    )
    k.set_acl(acl)
    gs_url = 'https://storage.googleapis.com/%s/' % bucket_name
    if sent == size:
        return gs_url + k.key
    return False


# ########
# HELPERS
# ########


def generate_hash(key):
    """
    Generate hash for key
    """
    phash = generate_password_hash(key, get_settings()['secret'])
    return str(b64encode(phash), 'utf-8')[:10]  # limit len to 10, is sufficient
