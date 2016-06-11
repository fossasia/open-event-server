from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from ....helpers.data import DataManager,save_to_db
from ....helpers.data_getter import DataGetter

class EventsSpeakersView(ModelView):
    @expose('/', methods=('GET', 'POST'))
    def index_view(self, event_id):
        speakers = DataGetter.get_speakers(event_id)
        return self.render('/gentelella/admin/event/speaker/display.html',
                           speakers=speakers, event_id=event_id)

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self, event_id):
        return self.render('/gentelella/admin/event/speaker/new.html', event_id=event_id)

    @expose('/<speaker_id>/delete/', methods=('POST',))
    def delete_view(self, event_id,speaker_id):
        return ''

    @expose('/<speaker_id>/edit/', methods=('POST', 'GET'))
    def edit_view(self, event_id, speaker_id):
        return self.render('/gentelella/admin/event/speaker/edit.html', event_id=event_id)
