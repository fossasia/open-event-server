import os
from shutil import copyfile

from boto.s3.connection import S3Connection
from boto.s3.key import Key

from app.settings import get_settings


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
        'photo': 'events/{event_id}/speakers/{id}/photo'
    },
    'event': {
        'logo': 'events/{event_id}/logo',
        'background_url': 'events/{event_id}/background'
    },
    'sponsors': {
        'logo': 'events/{event_id}/sponsors/{id}/logo'
    },
    'tracks': {
        'track_image_url': 'events/{event_id}/tracks/{id}/track_image'
    },
    'user': {
        'avatar': 'users/{user_id}/avatar'
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
        f.write(self.data)
        f.close()


#########
# MAIN
#########

def upload(file, key, **kwargs):
    """
    Upload handler
    """
    # refresh settings
    bucket_name = get_settings()['aws_bucket_name']
    aws_key = get_settings()['aws_key']
    aws_secret = get_settings()['aws_secret']
    storage_place = get_settings()['storage_place']
    # upload
    if bucket_name and aws_key and aws_secret and storage_place == 's3':
        return upload_to_aws(bucket_name, aws_key, aws_secret, file, key, **kwargs)
    else:
        return upload_local(file, key, **kwargs)


def upload_local(file, key, **kwargs):
    """
    Uploads file locally. Base dir - static/media/
    """
    basename, ext = os.path.splitext(file.filename)
    file_path = 'static/media/' + key + ext
    dir_path = file_path.rsplit('/', 1)[0]
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    file.save(file_path)
    return '/serve_' + file_path


def upload_to_aws(bucket_name, aws_key, aws_secret, file, key, acl='public-read'):
    """
    Uploads to AWS at key
    http://{bucket}.s3.amazonaws.com/{key}
    """
    conn = S3Connection(aws_key, aws_secret)
    bucket = conn.get_bucket(bucket_name)
    k = Key(bucket)
    # generate key using key + extension
    basename, ext = os.path.splitext(file.filename)  # includes dot
    k.key = key
    key_name = key.rsplit('/')[-1]
    # set object settings
    file_data = file.read()
    size = len(file_data)
    sent = k.set_contents_from_string(
        file_data,
        headers={
            'Content-Disposition': 'attachment; filename=%s%s' % (key_name, ext)
        }
    )
    k.set_acl(acl)
    s3_url = 'https://%s.s3.amazonaws.com/' % (bucket_name)
    if sent == size:
        return s3_url + k.key
    return False
