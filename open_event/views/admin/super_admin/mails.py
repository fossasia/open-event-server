from flask_admin import expose

from open_event.helpers.system_mails import MAILS
from super_admin_base import SuperAdminBaseView


class SuperAdminMailsView(SuperAdminBaseView):
    @expose('/')
    def index_view(self):
        return self.render(
            '/gentelella/admin/super_admin/mails/mails.html',
            mails=MAILS
        )
