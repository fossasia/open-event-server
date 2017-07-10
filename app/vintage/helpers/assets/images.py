import os
import uuid

import PIL
from PIL import Image
from flask import current_app as app
from app.helpers.storage import upload, UploadedFile, generate_hash


def get_image_file_name():
    return str(uuid.uuid4())


def get_path_of_temp_url(url):
    """
    Get the absolute path on the filesystem of the temp image URL
    :param url:
    :return:
    """
    return '{}/static/{}'.format(app.config['BASE_DIR'], url[len('/serve_static/'):])


def save_event_image(image_url, upload_path, ext='png', remove_after_upload=False):
    """
    Save the image
    :param ext:
    :param remove_after_upload:
    :param upload_path:
    :param image_url:
    :return:
    """
    filename = '{filename}.{ext}'.format(filename=get_image_file_name(), ext=ext)
    file_path = get_path_of_temp_url(image_url)
    logo_file = UploadedFile(file_path, filename)
    url = upload(logo_file, upload_path)
    if remove_after_upload:
        os.remove(file_path)
    return url if url else ''


def save_resized_image(image_file, basewidth, aspect, height_size, upload_path,
                       ext='jpg', remove_after_upload=False):
    """
    Save the resized version of the background image
    :param upload_path:
    :param ext:
    :param remove_after_upload:
    :param height_size:
    :param aspect:
    :param basewidth:
    :param image_file:
    :return:
    """
    filename = '{filename}.{ext}'.format(filename=get_image_file_name(), ext=ext)

    img = Image.open(image_file)
    if aspect == 'on':
        width_percent = (basewidth / float(img.size[0]))
        height_size = int((float(img.size[1]) * float(width_percent)))

    img = img.resize((basewidth, height_size), PIL.Image.ANTIALIAS)

    temp_file_relative_path = 'static/media/temp/' + generate_hash(str(image_file)) + get_image_file_name() + '.jpg'
    temp_file_path = app.config['BASE_DIR'] + '/' + temp_file_relative_path

    img.save(temp_file_path)

    file = UploadedFile(file_path=temp_file_path, filename=filename)

    if remove_after_upload:
        os.remove(image_file)

    uploaded_url = upload(file, upload_path)

    os.remove(temp_file_path)

    return uploaded_url


