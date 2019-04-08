from flask import send_file, Blueprint
import shutil
import uuid
import tempfile
import os

admin_blueprint = Blueprint('admin_blueprint', __name__, url_prefix='/v1/admin/content/translations/all')
temp_dir = tempfile.gettempdir()
translations_dir = 'app/translations'

@admin_blueprint.route('/', methods=['GET'])
def download_translations():
    """Admin Translations Downloads"""
    uuid_literal = uuid.uuid4()
    zip_file = "translations{}".format(uuid_literal)
    zip_file_ext = zip_file+'.zip'
    shutil.make_archive(zip_file, "zip", translations_dir)
    shutil.move(zip_file_ext, temp_dir)
    path_to_zip = os.path.join(temp_dir, zip_file_ext)
    from .helpers.tasks import delete_translations
    delete_translations.apply_async(path_to_zip, countdown=600)
    return send_file(path_to_zip,  mimetype='application/zip',
                     as_attachment=True,
                     attachment_filename='translations.zip')
