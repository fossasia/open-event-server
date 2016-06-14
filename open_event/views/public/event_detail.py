from flask.ext.restplus import abort
from flask_admin import BaseView, expose
from werkzeug.utils import redirect

from ...helpers.data_getter import DataGetter

class EventDetailView(BaseView):

    @expose('/')
    def display_default(self):
        return redirect("/browse")

    @expose('/<event_id>')
    def display_event_detail_home(self, event_id):
        event = DataGetter.get_event(event_id=event_id)
        if not event or event.state != 'Published':
            abort(404)
        accepted_sessions = DataGetter.get_sessions(event_id)

        return self.render('/gentelella/guest/event/details.html', event=event, accepted_sessions=accepted_sessions)

