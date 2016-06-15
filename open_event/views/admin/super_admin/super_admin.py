from flask import request, url_for, redirect
from flask_admin import expose
from flask_admin import BaseView
from flask.ext import login
from ....helpers.data import DataManager
from ....helpers.data_getter import DataGetter
from open_event.helpers.helpers import get_latest_heroku_release, get_commit_info

class SuperAdminView(BaseView):

    def is_accessible(self):
        return login.current_user.is_authenticated

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('admin.login_view', next=request.url))

    @expose('/')
    def index_view(self):
        events = DataGetter.get_all_events()[:5]
        version = get_latest_heroku_release()
        commit_number = version['description'].split(' ')[1]
        commit_info = get_commit_info(commit_number)
        return self.render('/gentelella/admin/super_admin/dashboard.html',
                           events=events, version=version, commit_info=commit_info)
