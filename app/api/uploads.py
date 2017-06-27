from flask import Blueprint
from flask import make_response, request, jsonify, abort
from flask_jwt import jwt_required
from app.api.helpers.files import uploaded_image, uploaded_file
from app.api.helpers.storage import UPLOAD_PATHS, upload_local, upload
import uuid

upload_routes = Blueprint('upload', __name__, url_prefix='/v1/upload')


@upload_routes.route('/image', methods=['POST'])
@jwt_required()
def upload_image():
    image = request.json['data']
    extension = '.{}'.format(image.split(";")[0].split("/")[1])
    image_file = uploaded_image(extension=extension, file_content=image)
    force_local = request.args.get('force_local', 'false')
    if force_local == 'true':
        image_url = upload_local(
            image_file,
            UPLOAD_PATHS['temp']['image'].format(uuid=uuid.uuid4())
        )
    else:
        image_url = upload(
            image_file,
            UPLOAD_PATHS['temp']['image'].format(uuid=uuid.uuid4())
        )
    return jsonify({"url": image_url})


@upload_routes.route('/files', methods=['POST'])
@jwt_required()
def upload_file():
    force_local = request.args.get('force_local', 'false')
    if 'file' in request.files:
        files = request.files['file']
        file_uploaded = uploaded_file(files=files)
        if force_local == 'true':
            files_url = upload_local(
                file_uploaded,
                UPLOAD_PATHS['temp']['event'].format(uuid=uuid.uuid4())
            )
        else:
            files_url = upload(
                file_uploaded,
                UPLOAD_PATHS['temp']['event'].format(uuid=uuid.uuid4())
            )
    elif 'files[]' in request.files:
        files = request.files.getlist('files[]')
        files_uploaded = uploaded_file(files=files, multiple=True)
        files_url = []
        for file_uploaded in files_uploaded:
            if force_local == 'true':
                files_url.append(upload_local(
                    file_uploaded,
                    UPLOAD_PATHS['temp']['event'].format(uuid=uuid.uuid4())
                ))
            else:
                files_url.append(upload(
                    file_uploaded,
                    UPLOAD_PATHS['temp']['event'].format(uuid=uuid.uuid4())
                ))
    else:
        abort(
            make_response(jsonify(error="Bad Request"), 400)
        )

    return jsonify({"url": files_url})
