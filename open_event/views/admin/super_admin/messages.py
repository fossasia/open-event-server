from flask_admin import expose

from open_event.helpers.system_mails import MAILS
from open_event.helpers.system_notifications import NOTIFS
from super_admin_base import SuperAdminBaseView


class SuperAdminMessagesView(SuperAdminBaseView):
    @expose('/')
    def index_view(self):
        return self.render(
            '/gentelella/admin/super_admin/messages/messages.html',
            mails=MAILS,
            notifications=NOTIFS
        )
