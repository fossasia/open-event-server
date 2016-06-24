from flask_admin import expose
from super_admin_base import SuperAdminBaseView

from open_event.settings import get_settings


class SuperAdminSettingsView(SuperAdminBaseView):
    @expose('/')
    def index_view(self):
        settings = get_settings()
        return self.render(
            '/gentelella/admin/super_admin/settings/settings.html',
            settings=settings
        )
