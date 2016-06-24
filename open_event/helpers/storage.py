import os
from boto.s3.connection import S3Connection
from boto.s3.key import Key


BUCKET_NAME = os.environ.get('BUCKET_NAME')
if BUCKET_NAME:
    S3_URL = 'https://%s.s3.amazonaws.com/' % (BUCKET_NAME)
AWS_KEY = os.environ.get('AWS_KEY')
AWS_SECRET = os.environ.get('AWS_SECRET')


def upload(file, key, **kwargs):
    """
    Upload handler
    """
    if BUCKET_NAME and AWS_KEY and AWS_SECRET:
        return upload_to_aws(file, key, **kwargs)
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


def upload_to_aws(file, key, acl='public-read'):
    """
    Uploads to AWS at key
    http://{bucket}.s3.amazonaws.com/{key}
    """
    conn = S3Connection(AWS_KEY, AWS_SECRET)
    bucket = conn.get_bucket(BUCKET_NAME)
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
    if sent == size:
        return S3_URL + k.key
    return False


if __name__ == '__main__':
    f = open('storage.py', 'r')
    upload_to_aws(f, 'test')
