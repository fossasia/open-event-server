from flask import request
from flask.ext.restplus import abort
from flask_admin import BaseView, expose
from werkzeug.utils import redirect

from ...helpers.data_getter import DataGetter

def get_published_event_or_abort(event_id):
    event = DataGetter.get_event(event_id=event_id)
    if not event or (event.state != u'Published' and event.state != 'Published'):
        abort(404)
    return event

class EventDetailView(BaseView):

    @expose('/')
    def display_default(self):
        return redirect("/browse")

    @expose('/<int:event_id>/')
    def display_event_detail_home(self, event_id):
        event = get_published_event_or_abort(event_id)
        accepted_sessions = DataGetter.get_sessions(event_id)
        return self.render('/gentelella/guest/event/details.html', event=event, accepted_sessions=accepted_sessions)

    @expose('/<int:event_id>/sessions/')
    def display_event_sessions(self, event_id):
        event = get_published_event_or_abort(event_id)
        sessions = DataGetter.get_sessions(event_id)
        return self.render('/gentelella/guest/event/sessions.html', event=event, sessions=sessions)

    @expose('/<int:event_id>/<slug>/')
    def display_event_detail_home_slugged(self, event_id, slug):
        return self.display_event_detail_home(event_id)

    @expose('/<int:event_id>/<slug>/sessions/')
    def display_event_sessions_slugged(self, event_id, slug):
        return self.display_event_sessions(event_id)
