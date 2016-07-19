from flask_admin import expose

from app.views.admin.super_admin.super_admin_base import SuperAdminBaseView



class SuperAdminModulesView(SuperAdminBaseView):

    @expose('/')
    def index_view(self):
        return ''
