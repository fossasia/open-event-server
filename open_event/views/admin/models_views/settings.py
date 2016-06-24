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

    @expose('/edit/event/<event_id>', methods=('GET', 'POST'))
    def edit_view(self, event_id):
        if request.method == 'POST':
            settings = DataManager.add_email_notification_settings(request.form, login.current_user.id, event_id)
            return redirect(url_for('settings.index_view'))
        event = DataGetter.get_event(event_id)
        settings = DataGetter.get_email_notification_settings_by_event_id(login.current_user.id, event_id)
        return self.render('/gentelella/admin/settings/edit.html', settings=settings, event=event)
