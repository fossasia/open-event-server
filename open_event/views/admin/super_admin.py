import flask_login
from flask_admin import BaseView, expose

from open_event.helpers.helpers import get_latest_heroku_release, get_commit_info

class SuperAdminView(BaseView):

    @expose('/')
    @flask_login.login_required
    def display_my_sessions_view(self):
        version = get_latest_heroku_release()
        commit_number = version['description'].split(' ')[1]
        commit_info = get_commit_info(commit_number)
        return self.render('gentelella/admin/current_version.html',
                           version=version, commit_info=commit_info)
