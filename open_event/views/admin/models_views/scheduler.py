from flask_admin import BaseView, expose
from ....helpers.data_getter import DataGetter

class SchedulerView(BaseView):
    @expose('/')
    def display_view(self, event_id):
        sessions = DataGetter.get_sessions_by_event_id(event_id)
        event = DataGetter.get_event(event_id)
        return self.render('/gentelella/admin/event/scheduler/scheduler.html', sessions=sessions, event=event)
