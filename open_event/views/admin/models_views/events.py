from flask import request, url_for, redirect
from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from flask.ext import login
from ....helpers.data import DataManager
from ....helpers.data_getter import DataGetter


class EventsView(ModelView):

    def is_accessible(self):
        return login.current_user.is_authenticated

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('admin.login_view', next=request.url))

    @expose('/')
    def index_view(self):
        events = DataGetter.get_user_events()
        return self.render('/gentelella/admin/event/index.html',
                           events=events)

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        if request.method == 'POST':
            event = DataManager.create_event(request.form)
            return redirect(url_for('.details_view', event_id=event.id))
        return self.render('/gentelella/admin/event/new/new.html')

    @expose('/<event_id>/', methods=('GET', 'POST'))
    def details_view(self, event_id):
        event = DataGetter.get_event(event_id)

        return self.render('/gentelella/admin/event/details/details.html', event=event)

    @expose('/<event_id>/delete/', methods=('GET','POST'))
    def delete_view(self, event_id):
        if request.method == "POST":
            DataManager.delete_event(event_id)
        return redirect(url_for('.index_view'))
