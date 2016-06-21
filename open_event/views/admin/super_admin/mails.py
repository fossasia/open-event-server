from flask_admin import expose

from open_event.helpers.data_getter import DataGetter
from super_admin_base import SuperAdminBaseView


class SuperAdminMailsView(SuperAdminBaseView):
    @expose('/')
    def index_view(self):
        mails = DataGetter.get_all_mails(count=300)
        return self.render('/gentelella/admin/super_admin/mails/mails.html', mails=mails)
