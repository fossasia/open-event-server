from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from ....helpers.data import DataManager
from ....helpers.data_getter import DataGetter
from ....helpers.roles import role_required, Role
from flask.ext import login
from flask import request, url_for, redirect, flash

class EventsView(ModelView):

    def is_accessible(self):
        return login.current_user.is_authenticated

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('admin.login_view', next=request.url))

    @expose('/')
    def index_view(self):
        # print DataGetter.get_all_users_events_roles().all()
        events = DataGetter.get_user_events()
        print events, "dsadsaa"

        return self.render('/gentelella/admin/event/index.html',
                           events=events)

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        DataManager.create_event_test()
        print dir(request)
        print request.values
        print request.query_string
        print request.form

        return self.render('/gentelella/admin/event/new.html')

    @expose('/<event_id>/details/', methods=('GET', 'POST'))
    def details_view(self, event_id):
        pass

    @expose('/<event_id>/edit/', methods=('GET', 'POST'))
    @role_required(roles=(Role.organizer,))
    def edit_view(self, event_id):
        return ''

    @expose('/<event_id>/delete/', methods=('GET', 'POST'))
    def delete_view(self, event_id):
        return ''

