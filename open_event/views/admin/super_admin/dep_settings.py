from flask_admin import expose
from super_admin_base import SuperAdminBaseView


class SuperAdminSettingsView(SuperAdminBaseView):
    @expose('/')
    def index_view(self):
        return self.render(
            '/gentelella/admin/super_admin/settings/settings.html',
        )
