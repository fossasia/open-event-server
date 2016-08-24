from flask_admin import expose
from flask import redirect, request, url_for

from app.helpers.system_mails import MAILS
from app.helpers.system_notifications import NOTIFS
from super_admin_base import SuperAdminBaseView, MESSAGES

from ....helpers.data_getter import DataGetter
from ....helpers.data import DataManager


class SuperAdminMessagesView(SuperAdminBaseView):
    PANEL_NAME = MESSAGES

    @expose('/')
    def index_view(self):
        message_settings = DataGetter.get_all_message_setting()
        return self.render(
            '/gentelella/admin/super_admin/messages/messages.html',
            mails=MAILS,
            notifications=NOTIFS,
            message_settings=message_settings
        )

    @expose('/update', methods=['POST'])
    def update_view(self):
        if request.method == 'POST':
            DataManager.create_or_update_message_settings(request.form)
        return redirect(url_for('sadmin_messages.index_view'))
