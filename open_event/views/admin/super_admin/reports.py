from flask_admin import expose

from open_event.views.admin.super_admin.super_admin_base import SuperAdminBaseView


class SuperAdminReportsView(SuperAdminBaseView):
    @expose('/')
    def index_view(self):
        return self.render('/gentelella/admin/super_admin/reports/reports.html')
