import base64
import io
import os
import urllib.parse
import urllib.request
import uuid

import PIL
import requests
from flask import current_app
from PIL import Image
from sqlalchemy.orm.exc import NoResultFound
from weasyprint import HTML
from xhtml2pdf import pisa

from app.api.helpers.ICalExporter import ICalExporter
from app.api.helpers.storage import UPLOAD_PATHS, UploadedFile, generate_hash, upload
from app.models.image_size import ImageSizes
from app.settings import get_settings


def get_file_name():
    return str(uuid.uuid4())


def uploaded_image(extension='.png', file_content=None):
    filename = get_file_name() + extension
    filedir = current_app.config.get('BASE_DIR') + '/static/uploads/'
    if not os.path.isdir(filedir):
        os.makedirs(filedir)
    file_path = filedir + filename
    file = open(file_path, "wb")
    file.write(base64.b64decode(file_content.split(",")[1]))
    file.close()
    return UploadedFile(file_path, filename)


def uploaded_file(files, multiple=False):
    if multiple:
        files_uploaded = []
        for file in files:
            extension = file.filename.split('.')[1]
            filename = get_file_name() + '.' + extension
            filedir = current_app.config.get('BASE_DIR') + '/static/uploads/'
            if not os.path.isdir(filedir):
                os.makedirs(filedir)
            file_path = filedir + filename
            file.save(file_path)
            files_uploaded.append(UploadedFile(file_path, filename))

    else:
        extension = files.filename.split('.')[1]
        filename = get_file_name() + '.' + extension
        filedir = current_app.config.get('BASE_DIR') + '/static/uploads/'
        if not os.path.isdir(filedir):
            os.makedirs(filedir)
        file_path = filedir + filename
        files.save(file_path)
        files_uploaded = UploadedFile(file_path, filename)

    return files_uploaded


def create_save_resized_image(
    image_file,
    basewidth=None,
    maintain_aspect=None,
    height_size=None,
    upload_path=None,
    ext='jpg',
    remove_after_upload=False,
    resize=True,
):
    """
    Create and Save the resized version of the background image
    :param resize:
    :param upload_path:
    :param ext:
    :param remove_after_upload:
    :param height_size:
    :param maintain_aspect:
    :param basewidth:
    :param image_file:
    :return:
    """
    if not image_file:
        return None
    filename = f'{get_file_name()}.{ext}'
    data = requests.get(image_file).content
    image_file = io.BytesIO(data)
    try:
        im = Image.open(image_file)
    except OSError:
        raise OSError("Corrupt/Invalid Image")

    # Convert to jpeg for lower file size.
    if im.format != 'JPEG':
        img = im.convert('RGB')
    else:
        img = im

    if resize:
        if maintain_aspect:
            width_percent = basewidth / float(img.size[0])
            height_size = int(float(img.size[1]) * float(width_percent))

        img = img.resize((basewidth, height_size), PIL.Image.ANTIALIAS)

    temp_file_relative_path = (
        'static/media/temp/' + generate_hash(str(image_file)) + get_file_name() + '.jpg'
    )
    temp_file_path = current_app.config['BASE_DIR'] + '/' + temp_file_relative_path
    dir_path = temp_file_path.rsplit('/', 1)[0]

    # create dirs if not present
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)

    img.save(temp_file_path)
    upfile = UploadedFile(file_path=temp_file_path, filename=filename)

    if remove_after_upload:
        # os.remove(image_file) No point in removing in memory file
        pass

    uploaded_url = upload(upfile, upload_path)
    os.remove(temp_file_path)

    return uploaded_url


def create_save_image_sizes(
    image_file, image_sizes_type, unique_identifier=None, folder=None
):
    """
    Save the resized version of the background image
    :param unique_identifier:
    :param image_sizes_type:
    :param image_file:
    :return:
    """
    try:
        image_sizes = ImageSizes.query.filter_by(type=image_sizes_type).one()
    except NoResultFound:
        image_sizes = ImageSizes(
            type=image_sizes_type,
            full_width=1300,
            full_height=500,
            full_aspect=True,
            full_quality=80,
            icon_width=75,
            icon_height=30,
            icon_aspect=True,
            icon_quality=80,
            thumbnail_width=500,
            thumbnail_height=200,
            thumbnail_aspect=True,
            thumbnail_quality=80,
            logo_width=500,
            logo_height=200,
            icon_size_width_height=35,
            icon_size_quality=80,
            small_size_width_height=50,
            small_size_quality=80,
            thumbnail_size_width_height=500,
        )

    # Get an unique identifier from uuid if not provided
    if unique_identifier is None:
        unique_identifier = get_file_name()

    if image_sizes_type == 'speaker-image':
        default_folder = 'users'
        folder = folder or default_folder

        thumbnail_aspect = icon_aspect = small_aspect = True
        thumbnail_basewidth = (
            thumbnail_height_size
        ) = image_sizes.thumbnail_size_width_height
        icon_basewidth = icon_height_size = image_sizes.icon_size_width_height
        small_basewidth = small_height_size = image_sizes.small_size_width_height
        original_upload_path = (
            UPLOAD_PATHS['user']['original']
            .format(identifier=unique_identifier)
            .replace(default_folder, folder)
        )
        small_upload_path = (
            UPLOAD_PATHS['user']['small']
            .format(identifier=unique_identifier)
            .replace(default_folder, folder)
        )
        thumbnail_upload_path = (
            UPLOAD_PATHS['user']['thumbnail']
            .format(identifier=unique_identifier)
            .replace(default_folder, folder)
        )
        icon_upload_path = (
            UPLOAD_PATHS['user']['icon']
            .format(identifier=unique_identifier)
            .replace(default_folder, folder)
        )
        new_images = {
            'original_image_url': create_save_resized_image(
                image_file, 0, 0, 0, original_upload_path, resize=False
            ),
            'small_image_url': create_save_resized_image(
                image_file,
                small_basewidth,
                small_aspect,
                small_height_size,
                small_upload_path,
            ),
            'thumbnail_image_url': create_save_resized_image(
                image_file,
                thumbnail_basewidth,
                thumbnail_aspect,
                thumbnail_height_size,
                thumbnail_upload_path,
            ),
            'icon_image_url': create_save_resized_image(
                image_file,
                icon_basewidth,
                icon_aspect,
                icon_height_size,
                icon_upload_path,
            ),
        }

    else:
        default_folder = 'events'
        folder = folder or default_folder

        large_aspect = image_sizes.full_aspect if image_sizes.full_aspect else False
        large_basewidth = image_sizes.full_width if image_sizes.full_width else 1300
        large_height_size = image_sizes.full_height if image_sizes.full_width else 500
        thumbnail_aspect = (
            image_sizes.thumbnail_aspect if image_sizes.full_aspect else False
        )
        thumbnail_basewidth = (
            image_sizes.thumbnail_width if image_sizes.thumbnail_width else 500
        )
        thumbnail_height_size = (
            image_sizes.thumbnail_height if image_sizes.thumbnail_height else 200
        )
        icon_aspect = image_sizes.icon_aspect if image_sizes.icon_aspect else False
        icon_basewidth = image_sizes.icon_width if image_sizes.icon_width else 75
        icon_height_size = image_sizes.icon_height if image_sizes.icon_height else 30
        original_upload_path = (
            UPLOAD_PATHS['event']['original']
            .format(identifier=unique_identifier)
            .replace(default_folder, folder)
        )
        large_upload_path = (
            UPLOAD_PATHS['event']['large']
            .format(identifier=unique_identifier)
            .replace(default_folder, folder)
        )
        thumbnail_upload_path = (
            UPLOAD_PATHS['event']['thumbnail']
            .format(identifier=unique_identifier)
            .replace(default_folder, folder)
        )
        icon_upload_path = (
            UPLOAD_PATHS['event']['icon']
            .format(identifier=unique_identifier)
            .replace(default_folder, folder)
        )
        new_images = {
            'original_image_url': create_save_resized_image(
                image_file, 0, 0, 0, original_upload_path, resize=False
            ),
            'large_image_url': create_save_resized_image(
                image_file,
                large_basewidth,
                large_aspect,
                large_height_size,
                large_upload_path,
            ),
            'thumbnail_image_url': create_save_resized_image(
                image_file,
                thumbnail_basewidth,
                thumbnail_aspect,
                thumbnail_height_size,
                thumbnail_upload_path,
            ),
            'icon_image_url': create_save_resized_image(
                image_file,
                icon_basewidth,
                icon_aspect,
                icon_height_size,
                icon_upload_path,
            ),
        }

    return new_images


def create_system_image(
    image_file=None, upload_path=None, unique_identifier=None, ext='jpg'
):
    """
    Create System Images for Event Topics
    :param upload_path:
    :param ext:
    :param remove_after_upload:
    :param image_file:
    :return:
    """
    # Get an unique identifier from uuid if not provided
    filename = f'{get_file_name()}.{ext}'
    if image_file:
        with urllib.request.urlopen(image_file) as img_data:
            image_file = io.BytesIO(img_data.read())
    else:
        file_relative_path = 'static/default_system_image.png'
        image_file = current_app.config['BASE_DIR'] + '/' + file_relative_path
    try:
        im = Image.open(image_file)
    except OSError:
        raise OSError("Corrupt/Invalid Image")

    # Convert to jpeg for lower file size.
    if im.format != 'JPEG':
        img = im.convert('RGB')
    else:
        img = im

    temp_file_relative_path = (
        'static/media/temp/' + generate_hash(str(image_file)) + get_file_name() + '.jpg'
    )
    temp_file_path = current_app.config['BASE_DIR'] + '/' + temp_file_relative_path
    dir_path = temp_file_path.rsplit('/', 1)[0]

    # create dirs if not present
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)

    img.save(temp_file_path)
    upfile = UploadedFile(file_path=temp_file_path, filename=filename)

    if not upload_path:
        upload_path = UPLOAD_PATHS['event_topic']['system_image'].format(
            event_topic_id=unique_identifier
        )

    uploaded_url = upload(upfile, upload_path)
    os.remove(temp_file_path)

    image = {'system_image_url': uploaded_url}
    return image


def make_frontend_url(path, parameters=None):
    """
    Create URL for frontend
    """
    settings = get_settings()
    frontend_url = urllib.parse.urlparse(settings.get('frontend_url') or '')

    full_path = '/'.join(x.strip('/') for x in (frontend_url.path, str(path)) if x)
    return urllib.parse.urlunparse(
        (
            frontend_url.scheme,
            frontend_url.netloc,
            full_path,
            '',
            str(urllib.parse.urlencode(parameters) if parameters else ''),
            '',
        )
    )


def create_save_pdf(
    pdf_data,
    key,
    dir_path='/static/uploads/pdf/temp/',
    identifier=get_file_name(),
    upload_dir='static/media/',
    new_renderer=False,
    extra_identifiers=None,
):
    """
    Create and Saves PDFs from html
    :param pdf_data:
    :return:
    """
    if extra_identifiers is None:
        extra_identifiers = {}
    filedir = current_app.config.get('BASE_DIR') + dir_path

    if not os.path.isdir(filedir):
        os.makedirs(filedir)

    filename = identifier + '.pdf'
    dest = filedir + filename

    pdf_content = pdf_data.encode('utf-8')
    if not new_renderer:
        with open(dest, 'wb') as file_:
            pisa.CreatePDF(io.BytesIO(pdf_content), file_)

    else:
        HTML(string=pdf_content).write_pdf(dest)

    uploaded_file = UploadedFile(dest, filename)
    upload_path = key.format(**{'identifier': identifier, **extra_identifiers})
    new_file = upload(uploaded_file, upload_path, upload_dir=upload_dir)
    # Removing old file created
    os.remove(dest)

    return new_file


def generate_ics_file(event_id, temp=True, include_sessions=True):
    """
    Generate the ICS file for the {event_id}
    """

    if temp:
        filedir = os.path.join(
            current_app.config.get('BASE_DIR'),
            f'static/uploads/temp/{event_id}/',
        )
    else:
        filedir = os.path.join(
            current_app.config.get('BASE_DIR'), 'static/uploads/' + event_id + '/'
        )

    if not os.path.isdir(filedir):
        os.makedirs(filedir)
    filename = "event_ical.ics"
    file_path = os.path.join(filedir, filename)
    with open(file_path, "w") as temp_file:
        temp_file.write(str(ICalExporter.export(event_id, include_sessions), 'utf-8'))

    return file_path
