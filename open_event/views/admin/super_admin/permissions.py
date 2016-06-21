from flask_admin import expose

from open_event.views.admin.super_admin.super_admin_base import SuperAdminBaseView


class SuperAdminPermissionsView(SuperAdminBaseView):

    @expose('/')
    def index_view(self):
        return self.render('/gentelella/admin/super_admin/permissions/permissions.html')
