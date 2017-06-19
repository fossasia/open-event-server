import uuid
from app.api.helpers.storage import UploadedFile
from flask import current_app


def get_image_file_name():
    return str(uuid.uuid4())


def uploaded_image(extension='.png', file_content=None):
    filename = get_image_file_name() + extension
    file_path = current_app.config.get('BASE_DIR') + '/static/uploads/' + filename
    file = open(file_path, "wb")
    file.write(file_content.split(",")[1].decode('base64'))
    file.close()
    return UploadedFile(file_path, filename)
