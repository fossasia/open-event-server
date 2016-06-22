from flask_admin import expose

from open_event.helpers.data_getter import DataGetter
from super_admin_base import SuperAdminBaseView


class SuperAdminLogsView(SuperAdminBaseView):
    @expose('/')
    def index_view(self):
        mails = DataGetter.get_all_mails(count=300)
        activities = DataGetter.get_all_activities(count=400)
        return self.render(
            '/gentelella/admin/super_admin/logs/logs.html',
            mails=mails,
            activities=activities
        )
