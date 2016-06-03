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

    @expose('/<int:event_id>/', methods=('GET', 'POST'))
    def details_view(self, event_id):
        event = DataGetter.get_event(event_id)
        return self.render('/gentelella/admin/event/details/details.html', event=event)

    @expose('/<int:event_id>/edit/', methods=('GET', 'POST'))
    def edit_view(self, event_id):
        event = DataGetter.get_event(event_id)
        session_types = DataGetter.get_session_types_by_event_id(event_id)
        tracks = DataGetter.get_tracks(event_id)
        social_links = DataGetter.get_social_links_by_event_id(event_id)
        if request.method == 'GET':
            return self.render('/gentelella/admin/event/edit/edit.html', event=event, session_types=session_types,
                               tracks=tracks, social_links=social_links)
        if request.method == "POST":
            event = DataManager.edit_event(request.form, event_id, event, session_types, tracks, social_links)
            return self.render('/gentelella/admin/event/details/details.html', event=event)

    @expose('/<event_id>/delete/', methods=('GET',))
    def delete_view(self, event_id):
        if request.method == "GET":
            DataManager.delete_event(event_id)
        return redirect(url_for('.index_view'))

    @expose('/completed/', methods=('GET',))
    def completed_events_view(self):
        events = DataGetter.get_completed_events()
        return self.render('/gentelella/admin/event/completed_events.html', events=events)

    @expose('/current/', methods=('GET',))
    def current_view(self):
        events = DataGetter.get_current_events()
        return self.render('/gentelella/admin/event/current_events.html', events=events)
