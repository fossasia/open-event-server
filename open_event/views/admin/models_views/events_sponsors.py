from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from ....helpers.data import DataManager,save_to_db
from ....helpers.data_getter import DataGetter

class EventsSponsorsView(ModelView):
    @expose('/', methods=('GET', 'POST'))
    def index_view(self, event_id):
        sponsors = DataGetter.get_sponsors(event_id)
        return self.render('/gentelella/admin/event/sponsor/display.html',
                           sponsors=sponsors, event_id=event_id)

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self, event_id):
        return self.render('/gentelella/admin/event/sponsor/new.html', event_id=event_id)

    @expose('/<speaker_id>/delete/', methods=('POST',))
    def delete_view(self, event_id,sponsor_id):
        return ''

    @expose('/<speaker_id>/edit/', methods=('POST', 'GET'))
    def edit_view(self, event_id, sponsor_id):
        return self.render('/gentelella/admin/event/sponsor/edit.html', event_id=event_id)
