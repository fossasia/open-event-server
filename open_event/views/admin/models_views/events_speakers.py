from flask_admin import expose
from flask_admin.contrib.sqla import ModelView


class EventsSpeakersView(ModelView):
    @expose('/', methods=('GET', 'POST'))
    def index_view(self, event_id):
        return ''

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self, event_id):
        return ''

    @expose('/<speaker_id>/delete/', methods=('POST',))
    def delete_view(self, event_id,speaker_id):
        return ''

    @expose('/<speaker_id>/edit/', methods=('POST', 'GET'))
    def edit_view(self, event_id, speaker_id):
        return ''
