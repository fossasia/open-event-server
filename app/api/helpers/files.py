import uuid
from app.api.helpers.storage import UploadedFile
from flask import current_app
import os


def get_image_file_name():
    return str(uuid.uuid4())


def uploaded_image(extension='.png', file_content=None):
    filename = get_image_file_name() + extension
    filedir = current_app.config.get('BASE_DIR') + '/static/uploads/'
    if not os.path.isdir(filedir):
        os.makedirs(filedir)
    file_path = filedir + filename
    file = open(file_path, "wb")
    file.write(file_content.split(",")[1].decode('base64'))
    file.close()
    return UploadedFile(file_path, filename)


def uploaded_file(files, multiple=False):
    if multiple:
        files_uploaded = []
        for file in files:
            filename = file.filename
            filedir = current_app.config.get('BASE_DIR') + '/static/uploads/'
            if not os.path.isdir(filedir):
                os.makedirs(filedir)
            file_path = filedir + filename
            file.save(file_path)
            files_uploaded.append(UploadedFile(file_path, filename))

    else:
        filename = files.filename
        filedir = current_app.config.get('BASE_DIR') + '/static/uploads/'
        if not os.path.isdir(filedir):
            os.makedirs(filedir)
        file_path = filedir + filename
        files.save(file_path)
        files_uploaded = UploadedFile(file_path, filename)

    return files_uploaded
