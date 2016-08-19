from flask import redirect, request, url_for, jsonify
from flask_admin import expose
from app.views.admin.super_admin.super_admin_base import SuperAdminBaseView, CONTENT
from ....helpers.data_getter import DataGetter
from ....helpers.data import DataManager, delete_from_db, save_to_db
from ....models.custom_placeholder import CustomPlaceholder
from app.settings import get_settings, set_settings
from app.helpers.storage import upload, UploadedFile
from app.helpers.helpers import uploaded_file
import PIL
from PIL import Image
import shutil
import os


class SuperAdminContentView(SuperAdminBaseView):
    PANEL_NAME = CONTENT

    @expose('/', methods=('GET', 'POST'))
    def index_view(self):
        placeholder_images = DataGetter.get_event_default_images()
        pages = DataGetter.get_all_pages()
        custom_placeholder = DataGetter.get_custom_placeholders()
        settings = get_settings()
        if request.method == 'POST':
            dic = dict(request.form.copy())
            for key, value in dic.items():
                settings[key] = value[0]
                set_settings(**settings)
        return self.render(
            '/gentelella/admin/super_admin/content/content.html', pages=pages, settings=settings,
            placeholder_images=placeholder_images, custom_placeholder=custom_placeholder
        )

    @expose('/create/files/placeholder', methods=('POST',))
    def placeholder_upload(self):
        if request.method == 'POST':
            placeholder_image = request.form['placeholder']
            filename = request.form['file_name']
            print filename
            if placeholder_image:
                placeholder_file = uploaded_file(file_content=placeholder_image)
                placeholder = upload(
                    placeholder_file,
                    'placeholders/original/'+filename
                )
                temp_img_file = placeholder.replace('/serve_', '')

                basewidth = 300
                img = Image.open(temp_img_file)
                wpercent = (basewidth / float(img.size[0]))
                hsize = int((float(img.size[1]) * float(wpercent)))
                img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
                os.mkdir('static/media/temp/')
                img.save('static/media/temp/temp.png')
                file_name = temp_img_file.rsplit('/', 1)[1]
                thumbnail_file = UploadedFile(file_path=temp_img_file, filename=file_name)
                background_thumbnail_url = upload(
                    thumbnail_file,
                    'placeholders/thumbnail/'+filename
                )
                shutil.rmtree(path='static/media/temp/')
                print request.form['name']
                placeholder_db = CustomPlaceholder(name=request.form['name'],
                                                   url=placeholder,
                                                   thumbnail=background_thumbnail_url,
                                                   copyright=request.form['copyright'],
                                                   origin=request.form['origin'])
                save_to_db(placeholder_db, 'User notification saved')

                return jsonify({'status': 'ok', 'placeholder': placeholder})
            else:
                return jsonify({'status': 'no logo'})

    @expose('/update_placeholder', methods=('POST',))
    def placeholder_upload_details(self):
        pass

    @expose('/pages/create', methods=['POST'])
    def create_view(self):
        DataManager.create_page(request.form)
        return redirect(url_for('sadmin_content.index_view'))

    @expose('/pages/<page_id>', methods=['GET', 'POST'])
    def details_view(self, page_id):
        page = DataGetter.get_page_by_id(page_id)
        if request.method == 'POST':
            DataManager().update_page(page, request.form)
            return redirect(url_for('sadmin_content.details_view', page_id=page_id))
        pages = DataGetter.get_all_pages()
        return self.render('/gentelella/admin/super_admin/content/content.html',
                           pages=pages,
                           current_page=page)

    @expose('/pages/<page_id>/trash', methods=['GET'])
    def trash_view(self, page_id):
        page = DataGetter.get_page_by_id(page_id)
        delete_from_db(page, "Page has already deleted")
        return redirect(url_for('sadmin_content.index_view'))
