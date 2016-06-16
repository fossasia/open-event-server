import os

from flask import request, url_for, redirect
from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from flask.ext import login
from ....helpers.data_getter import DataGetter
from flask_admin import BaseView


class SuperAdminEventsView(BaseView):
    def is_accessible(self):
        return login.current_user.is_authenticated

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('admin.login_view', next=request.url))

    @expose('/')
    def index_view(self):
        live_events = DataGetter.get_all_live_events()
        draft_events = DataGetter.get_all_draft_events()
        past_events = DataGetter.get_all_past_events()
        all_events = DataGetter.get_all_events()
        return self.render('/gentelella/admin/super_admin/events/events.html',
                           live_events=live_events,
                           draft_events=draft_events,
                           past_events=past_events,
                           all_events=all_events)
