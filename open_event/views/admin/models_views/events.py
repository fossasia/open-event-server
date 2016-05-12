from flask_admin import expose
from flask_admin.contrib.sqla import ModelView


class EventsView(ModelView):

    def is_accessible(self):
        return True

    @expose('/')
    def index_view(self):
        return self.render('/gentelella/admin/event/index.html')

    @expose('/new', methods=('GET', 'POST'))
    def create_view(self):
        return ''

    @expose('<event_id>/edit', methods=('GET', 'POST'))
    def edit_view(self):
        return ''

    @expose('<event_id>/delete', methods=('GET', 'POST'))
    def delete_view(self):
        return ''
