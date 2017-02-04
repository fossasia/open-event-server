import copy
import os
import shutil
import errno

import PIL
from PIL import Image
from babel.messages import frontend as babel
from flask import Blueprint
from flask import current_app as app
from flask import redirect, request, url_for, jsonify, render_template
from flask import send_from_directory
from flask import flash

from app.helpers.data import DataManager, delete_from_db, save_to_db
from app.helpers.data_getter import DataGetter
from app.helpers.helpers import uploaded_file
from app.helpers.storage import upload, UploadedFile
from app.models.custom_placeholder import CustomPlaceholder
from app.settings import get_settings, set_settings
from app.views.super_admin import check_accessible, CONTENT, list_navbar
from config import basedir, LANGUAGES

BASE_TRANSLATIONS_DIR = str(basedir) + "/app/translations"

sadmin_content = Blueprint('sadmin_content', __name__, url_prefix='/admin/content')


@sadmin_content.before_request
def verify_accessible():
    return check_accessible(CONTENT)


@sadmin_content.route('/', methods=('GET', 'POST'))
def index_view():
    placeholder_images = DataGetter.get_event_default_images()
    pages = DataGetter.get_all_pages()
    custom_placeholder = DataGetter.get_custom_placeholders()
    subtopics = DataGetter.get_event_subtopics()
    settings = get_settings()
    languages_copy = copy.deepcopy(LANGUAGES)
    try:
        languages_copy.pop("en")
    except:
        pass
    if request.method == 'POST':
        dic = dict(request.form.copy())
        for key, value in dic.items():
            settings[key] = value[0]
            set_settings(**settings)
        flash("Changes have been saved.")
    return render_template(
        'gentelella/super_admin/content/content.html', pages=pages, settings=settings,
        placeholder_images=placeholder_images, subtopics=subtopics, custom_placeholder=custom_placeholder,
        languages=languages_copy, navigation_bar=list_navbar()
    )


@sadmin_content.route('/create/files/placeholder/', methods=('POST',))
def placeholder_upload():
    if request.method == 'POST':
        placeholder_image = request.form['placeholder']
        filename = request.form['file_name']
        if placeholder_image:
            placeholder_file = uploaded_file(file_content=placeholder_image)
            placeholder = upload(
                placeholder_file,
                'placeholders/original/' + filename
            )
            temp_img_file = placeholder.replace('/serve_', '')

            basewidth = 300
            img = Image.open(temp_img_file)
            wpercent = (basewidth / float(img.size[0]))
            hsize = int((float(img.size[1]) * float(wpercent)))
            img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
            try:
                os.mkdir(app.config['TEMP_UPLOADS_FOLDER'])
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise exc
                pass
            img.save(app.config['TEMP_UPLOADS_FOLDER'] + '/temp.png')
            file_name = temp_img_file.rsplit('/', 1)[1]
            thumbnail_file = UploadedFile(file_path=temp_img_file, filename=file_name)
            background_thumbnail_url = upload(
                thumbnail_file,
                'placeholders/thumbnail/' + filename
            )
            shutil.rmtree(path=app.config['TEMP_UPLOADS_FOLDER'])
            placeholder_db = DataGetter.get_custom_placeholder_by_name(request.form['name'])
            if placeholder_db:
                placeholder_db.url = placeholder
                placeholder_db.thumbnail = background_thumbnail_url
            else:
                placeholder_db = CustomPlaceholder(name=request.form['name'],
                                                   url=placeholder,
                                                   thumbnail=background_thumbnail_url)
            save_to_db(placeholder_db, 'Custom Placeholder saved')

            return jsonify({'status': 'ok', 'placeholder': placeholder, 'id': placeholder_db.id})
        else:
            return jsonify({'status': 'no logo'})


@sadmin_content.route('/update_placeholder/', methods=('POST',))
def placeholder_upload_details():
    if request.method == 'POST':
        copyright_info = request.form['copyright']
        origin_info = request.form['origin']
        placeholder_id = request.form['placeholder_id']
        placeholder_db = DataGetter.get_custom_placeholder_by_id(placeholder_id)
        placeholder_db.copyright = copyright_info
        placeholder_db.origin = origin_info
        save_to_db(placeholder_db, 'Custom Placeholder updated')
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'error'})


@sadmin_content.route('/pages/create/', methods=['POST'])
def create_view():
    DataManager.create_page(request.form)
    return redirect(url_for('sadmin_content.index_view'))


@sadmin_content.route('/pages/<page_id>/', methods=['GET', 'POST'])
def details_view(page_id):
    page = DataGetter.get_page_by_id(page_id)
    if request.method == 'POST':
        DataManager().update_page(page, request.form)
        return redirect(url_for('sadmin_content.details_view', page_id=page_id))
    pages = DataGetter.get_all_pages()
    return render_template('gentelella/super_admin/content/content.html',
                           pages=pages,
                           current_page=page, navigation_bar=list_navbar())


@sadmin_content.route('/pages/<page_id>/trash/')
def trash_view(page_id):
    page = DataGetter.get_page_by_id(page_id)
    delete_from_db(page, "Page has already deleted")
    return redirect(url_for('sadmin_content.index_view'))


@sadmin_content.route('/update_translation/', methods=('POST',))
def upload_translation():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    extension = os.path.splitext(file.filename)[1]
    if file and extension == '.po':
        try:
            l_code = request.form["l_code"]
            file_destination = BASE_TRANSLATIONS_DIR + "/" + l_code + "/LC_MESSAGES"
            file.save(os.path.join(file_destination, "messages.po"))
            compiler = babel.compile_catalog()
            compiler.input_file = os.path.join(file_destination, "messages.po")
            compiler.output_file = os.path.join(file_destination, "messages.mo")
            compiler.run()
            return "Uploading and Compiling Done!"
        except Exception, e:
            return str(e)
    return "File extension not allowed"


@sadmin_content.route('/translation_uploads/<path:l_code>/')
def download(l_code):
    file_destination = BASE_TRANSLATIONS_DIR + "/" + l_code + "/LC_MESSAGES"
    return send_from_directory(directory=file_destination, filename="messages.po")
