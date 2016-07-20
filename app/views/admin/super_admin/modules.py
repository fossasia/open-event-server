from flask_admin import expose
from flask import request
from app.views.admin.super_admin.super_admin_base import SuperAdminBaseView
from app.helpers.data import DataManager


class SuperAdminModulesView(SuperAdminBaseView):

    @expose('/')
    def index_view(self):
        return self.render('/gentelella/admin/super_admin/modules/modules.html')

    @expose('/save')
    def modules_save_view(self):
        modules = DataManager.create_modules(request.form)
        return ''
