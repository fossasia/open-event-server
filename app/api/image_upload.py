from flask import Blueprint
from flask import url_for, redirect, request, current_app, jsonify
from flask_jwt import jwt_required
from flask import current_app as app
from app.api.helpers.images import uploaded_image
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
