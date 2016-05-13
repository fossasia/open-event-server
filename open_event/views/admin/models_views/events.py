from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from ....helpers.data import DataManager
from ....helpers.data_getter import DataGetter
from ....helpers.permission import role_required


class EventsView(ModelView):

    def is_accessible(self):
        return True

    @expose('/')
    def index_view(self):
        # print DataGetter.get_all_users_events_roles().all()
        print DataGetter.get_all_events()
        return self.render('/gentelella/admin/event/index.html')

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        DataManager.create_event_test()

        return ''

    @expose('/<event_id>/details/', methods=('GET', 'POST'))
    def details_view(self, event_id):
        pass

    @expose('/<event_id>/edit/', methods=('GET', 'POST'))
    @role_required(roles=('1',))
    def edit_view(self, event_id):
        return ''

    @expose('/<event_id>/delete/', methods=('GET', 'POST'))
    def delete_view(self, event_id):
        return ''

