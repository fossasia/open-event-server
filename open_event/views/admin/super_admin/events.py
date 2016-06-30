
from flask_admin import expose

from open_event.views.admin.super_admin.super_admin_base import SuperAdminBaseView
from ....helpers.data_getter import DataGetter
from flask import session
from datetime import timedelta

class SuperAdminEventsView(SuperAdminBaseView):

    @expose('/')
    def index_view(self):
        live_events = DataGetter.get_all_live_events()
        draft_events = DataGetter.get_all_draft_events()
        past_events = DataGetter.get_all_past_events()
        all_events = DataGetter.get_all_events()
        trash_events = DataGetter.get_trash_events()
        return self.render('/gentelella/admin/super_admin/events/events.html',
                           live_events=live_events,
                           draft_events=draft_events,
                           past_events=past_events,
                           all_events=all_events,
                           trash_events=trash_events)
