from flask_admin import expose

from open_event.views.admin.super_admin.super_admin_base import SuperAdminBaseView
from ....helpers.data_getter import DataGetter
from open_event.helpers.helpers import get_latest_heroku_release, get_commit_info


class SuperAdminView(SuperAdminBaseView):

    @expose('/')
    def index_view(self):
        events = DataGetter.get_all_events()[:5]
        version = get_latest_heroku_release()
        commit_number = None
        commit_info = None
        if version:
            commit_number = version['description'].split(' ')[1]
            commit_info = get_commit_info(commit_number)
        return self.render('/gentelella/admin/super_admin/widgets/index.html',
                           events=events, version=version, commit_info=commit_info)
