from flask.ext.admin import BaseView
from flask.ext.restplus import abort
from flask_admin import expose
from flask.ext import login
from flask import request, url_for, redirect, flash
from ....helpers.data import delete_from_db
from ....helpers.data_getter import DataGetter

def get_speaker_or_throw(speaker_id):
    session = DataGetter.get_speaker(speaker_id)
    if not session:
        abort(404)
    return session

class SpeakersView(BaseView):

    def is_accessible(self):
        return login.current_user.is_authenticated

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('admin.login_view', next=request.url))

    @expose('/')
    def index_view(self, event_id):
        speakers = DataGetter.get_speakers(event_id)
        event = DataGetter.get_event(event_id)
        return self.render('/gentelella/admin/event/speakers/base_speaker_table.html',
                           speakers=speakers, event_id=event_id, event=event)

    @expose('/<int:speaker_id>/')
    def display_view(self, event_id, speaker_id):
        speaker = get_speaker_or_throw(speaker_id)
        event = DataGetter.get_event(event_id)
        return self.render('/gentelella/admin/event/speakers/display.html',
                           speaker=speaker, event_id=event_id, event=event)

    @expose('/<int:speaker_id>/edit/', methods=('GET', 'POST'))
    def edit_view(self, event_id, speaker_id):
        speaker = get_speaker_or_throw(speaker_id)
        if request.method == 'GET':
            return self.render('/gentelella/admin/speakers/edit.html', speaker=speaker)
        if request.method == 'POST':

            return redirect(url_for('.index_view', event_id=event_id))

    @expose('/<int:speaker_id>/delete', methods=('GET',))
    def delete(self, event_id, speaker_id):
        speaker = get_speaker_or_throw(speaker_id)
        delete_from_db(speaker, 'Speaker Rejected')
        flash("The speaker has been deleted", "danger")
        return redirect(url_for('.index_view', event_id=event_id))
