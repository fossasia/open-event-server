from flask import redirect, request, url_for
from flask_admin import expose
from app.views.admin.super_admin.super_admin_base import SuperAdminBaseView, CONTENT
from ....helpers.data_getter import DataGetter
from ....helpers.data import DataManager, delete_from_db
from app.settings import get_settings, set_settings


class SuperAdminContentView(SuperAdminBaseView):
    PANEL_NAME = CONTENT

    @expose('/', methods=('GET', 'POST'))
    def index_view(self):
        placeholder_images = DataGetter.get_event_default_images()
        pages = DataGetter.get_all_pages()
        settings = get_settings()
        if request.method == 'POST':
            dic = dict(request.form.copy())
            for key, value in dic.items():
                settings[key] = value[0]
                set_settings(**settings)
        return self.render(
            '/gentelella/admin/super_admin/content/content.html', pages=pages, settings=settings,
            placeholder_images=placeholder_images
        )

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
