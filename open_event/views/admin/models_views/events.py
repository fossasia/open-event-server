from flask import request, url_for, redirect
from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from flask.ext import login
from ....helpers.data import DataManager, save_to_db
from ....helpers.data_getter import DataGetter
from datetime import datetime


class EventsView(ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('admin.login_view', next=request.url))

    @expose('/')
    def index_view(self):
        live_events = DataGetter.get_live_events()
        draft_events = DataGetter.get_draft_events()
        past_events = DataGetter.get_past_events()
        all_events = DataGetter.get_all_events()
        return self.render('/gentelella/admin/event/index.html',
                           live_events=live_events, draft_events=draft_events, past_events=past_events,
                           all_events=all_events)

    @expose('/create/', methods=('GET', 'POST'))
    def create_view(self):
        session_columns = DataGetter.get_session_columns()
        speaker_columns = DataGetter.get_speaker_columns()
        if request.method == 'POST':
            event = DataManager.create_event(request.form)
            if event:
                return redirect(url_for('.details_view', event_id=event.id))
            return redirect(url_for('.index_view'))
        return self.render('/gentelella/admin/event/new/new.html',
                           session_columns=session_columns,
                           speaker_columns=speaker_columns)

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
        microlocations = DataGetter.get_microlocations(event_id)
        call_for_speakers = DataGetter.get_call_for_papers(event_id)
        sponsors = DataGetter.get_sponsors(event_id)
        session_columns = DataGetter.get_session_columns()
        speaker_columns = DataGetter.get_speaker_columns()
        if request.method == 'GET':
            return self.render('/gentelella/admin/event/edit/edit.html', event=event, session_types=session_types,
                               tracks=tracks, social_links=social_links, microlocations=microlocations,
                               call_for_speakers=call_for_speakers, sponsors=sponsors, session_columns=session_columns,
                               speaker_columns=speaker_columns)
        if request.method == "POST":
            event = DataManager.edit_event(request.form, event_id, event, session_types, tracks, social_links,
                                           microlocations, call_for_speakers, sponsors)
            return self.render('/gentelella/admin/event/details/details.html', event=event)

    @expose('/<event_id>/delete/', methods=('GET',))
    def delete_view(self, event_id):
        if request.method == "GET":
            DataManager.delete_event(event_id)
        return redirect(url_for('.index_view'))

    @expose('/<int:event_id>/update/', methods=('POST',))
    def save_closing_date(self, event_id):
        event = DataGetter.get_event(event_id)
        event.closing_datetime = request.form['closing_datetime']
        save_to_db(event, 'Closing Datetime Updated')
        return self.render('/gentelella/admin/event/details/details.html', event=event)
