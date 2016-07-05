from flask import request, url_for, redirect
from flask.ext.admin import BaseView
from flask_admin import expose
from flask.ext import login

from ....helpers.data import DataManager
from ....helpers.data_getter import DataGetter


class SettingsView(BaseView):

    def is_accessible(self):
        return login.current_user.is_authenticated

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('admin.login_view', next=request.url))

    @expose('/')
    def index_view(self):
        events = DataGetter.get_all_events()
        settings = DataGetter.get_email_notification_settings(login.current_user.id)
        return self.render('/gentelella/admin/settings/index.html',
                           settings=settings, events=events)


    @expose('/toggle', methods=('GET', 'POST'))
    def toggle_view(self):
        if request.method == 'POST':
            value = request.form.get('value')
            print value
            settings = DataManager.toggle_email_notification_settings(login.current_user.id, value)
            return "success"
