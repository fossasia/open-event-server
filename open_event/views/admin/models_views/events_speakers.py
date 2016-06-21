from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from ....helpers.data import DataManager,save_to_db
from ....helpers.data_getter import DataGetter
from open_event.helpers.permission_decorators import *

class EventsSpeakersView(ModelView):
    @expose('/', methods=('GET', 'POST'))
    def index_view(self, event_id):
        speakers = DataGetter.get_speakers(event_id)
        event = DataGetter.get_event(event_id)
        return self.render('/gentelella/admin/event/speaker/display.html',
                           speakers=speakers, event_id=event_id, event=event)

    @expose('/create/', methods=('GET', 'POST'))
    @can_access
    def create_view(self, event_id):
        event = DataGetter.get_event(event_id)
        return self.render('/gentelella/admin/event/speaker/new.html', event_id=event_id, event=event)

    @expose('/<speaker_id>/delete/', methods=('POST',))
    @can_access
    def delete_view(self, event_id,speaker_id):
        return ''

    @expose('/<speaker_id>/edit/', methods=('POST', 'GET'))
    @can_access
    def edit_view(self, event_id, speaker_id):
        event = DataGetter.get_event(event_id)
        return self.render('/gentelella/admin/event/speaker/edit.html', event_id=event_id, event=event)
