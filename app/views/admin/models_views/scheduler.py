from datetime import datetime

from flask import url_for, flash
from flask_admin import BaseView, expose
from werkzeug.utils import redirect

from app.helpers.data import save_to_db
from ....helpers.data_getter import DataGetter

class SchedulerView(BaseView):

    @expose('/')
    def display_view(self, event_id):
        sessions = DataGetter.get_sessions_by_event_id(event_id)
        event = DataGetter.get_event(event_id)
        return self.render('/gentelella/admin/event/scheduler/scheduler.html', sessions=sessions, event=event)

    @expose('/publish')
    def publish(self, event_id):
        event = DataGetter.get_event(event_id)
        event.schedule_published_on = datetime.now()
        save_to_db(event, "Event schedule published")
        flash('The schedule has been published for this event', 'success')
        return redirect(url_for('.display_view', event_id=event_id))

    @expose('/unpublish')
    def unpublish(self, event_id):
        event = DataGetter.get_event(event_id)
        event.schedule_published_on = None
        save_to_db(event, "Event schedule unpublished")
        flash('The schedule has been unpublished for this event', 'success')
        return redirect(url_for('.display_view', event_id=event_id))
