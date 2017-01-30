import os
import time

import PIL
from PIL import Image
from flask import current_app as app
from app.helpers.storage import upload, UploadedFile


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
    filename = '{filename}.{ext}'.format(filename=time.time(), ext=ext)
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
    filename = '{filename}.{ext}'.format(filename=time.time(), ext=ext)

    img = Image.open(image_file)
    if aspect == 'on':
        width_percent = (basewidth / float(img.size[0]))
        height_size = int((float(img.size[1]) * float(width_percent)))

    img = img.resize((basewidth, height_size), PIL.Image.ANTIALIAS)
    img.save(image_file)
    file = UploadedFile(file_path=image_file, filename=filename)

    if remove_after_upload:
        os.remove(image_file)

    return upload(file, upload_path)


