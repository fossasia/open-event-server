import os

from flask.ext.admin import BaseView
from flask.ext.restplus import abort
from flask_admin import expose
from open_event.helpers.permission_decorators import *
from flask.ext import login
from flask import request, url_for, redirect, flash
from ....helpers.data import DataManager, save_to_db, delete_from_db
from ....helpers.data_getter import DataGetter
from werkzeug.utils import secure_filename
import json

def get_session_or_throw(session_id):
    session = DataGetter.get_session(session_id)
    if not session:
        abort(404)
    return session

class SessionsView(BaseView):

    def is_accessible(self):
        return login.current_user.is_authenticated

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('admin.login_view', next=request.url))

    @expose('/')
    def index_view(self, event_id):
        sessions = DataGetter.get_sessions_by_event_id(event_id)
        event = DataGetter.get_event(event_id)
        return self.render('/gentelella/admin/event/sessions/base_session_table.html',
                           sessions=sessions, event_id=event_id, event=event)

    @expose('/<int:session_id>/')
    def session_display_view(self, event_id, session_id):
        session = get_session_or_throw(session_id)
        event = DataGetter.get_event(event_id)
        return self.render('/gentelella/admin/event/sessions/display.html',
                           session=session, event_id=event_id, event=event)

    @expose('/create/', methods=('GET', 'POST'))
    @can_access
    def create_view(self, event_id):
        form_elems = DataGetter.get_custom_form_elements(event_id).first()
        if not form_elems:
            flash("Speaker and Session forms have been incorrectly configured for this event."
                  " Session creation has been disabled", "danger")
            return redirect(url_for('.index_view', event_id=event_id))
        speaker_form = json.loads(form_elems.speaker_form)
        session_form = json.loads(form_elems.session_form)
        event = DataGetter.get_event(event_id)
        if request.method == 'POST':
            speaker_img_file = ""
            slide_file = ""
            video_file = ""
            audio_file = ""
            if 'slides' in request.files and request.files['slides'].filename != '':
                slide_file = request.files['slides']
            if 'video' in request.files and request.files['video'].filename != '':
                video_file = request.files['video']
            if 'audio' in request.files and request.files['audio'].filename != '':
                audio_file = request.files['audio']
            if 'photo' in request.files and request.files['photo'].filename != '':
                speaker_img_file = request.files['photo']
            DataManager.add_session_to_event(request.form, event_id, speaker_img_file,
                                             slide_file, audio_file, video_file)
            return redirect(url_for('.index_view', event_id=event_id))
        return self.render('/gentelella/admin/event/sessions/new.html',
                           speaker_form=speaker_form, session_form=session_form, event=event)

    @expose('/new/<user_id>/<hash>/', methods=('GET', 'POST'))
    def new_view(self, event_id, user_id, hash):
        invite = DataGetter.get_invite_by_user_id(user_id)
        event = DataGetter.get_event(event_id)
        if invite and invite.hash == hash:
            if request.method == 'POST':
                DataManager.add_session_to_event(request.form, event_id)
                return redirect(url_for('.index_view', event_id=event_id))
            return self.render('/gentelella/admin/sessions/new.html', event=event)

    @expose('/<int:session_id>/invited/', methods=('GET', 'POST'))
    def invited_view(self, event_id, session_id):
        session = DataGetter.get_session(session_id)
        return self.render('/gentelella/admin/event/sessions/invited.html',
                           session=session, event_id=event_id)

    @expose('/<int:session_id>/speaker/', methods=('GET', 'POST'))
    def speaker_view(self, event_id, session_id):
        session = get_session_or_throw(session_id)
        form_elems = DataGetter.get_custom_form_elements(event_id)
        if request.method == 'POST':
            DataManager.add_speaker_to_session(request.form, event_id, session_id)
            return redirect(url_for('.index_view', event_id=event_id))
        return self.render('/gentelella/admin/event/sessions/speaker.html',
                           session=session, event_id=event_id, form_elems=form_elems)

    @expose('/<int:session_id>/edit/', methods=('GET', 'POST'))
    @can_access
    def edit_view(self, event_id, session_id):
        session = get_session_or_throw(session_id)
        form_elems = DataGetter.get_custom_form_elements(event_id).first()
        if not form_elems:
            flash("Speaker and Session forms have been incorrectly configured for this event."
                  " Session creation has been disabled", "danger")
            return redirect(url_for('.index_view', event_id=event_id))
        speaker_form = json.loads(form_elems.speaker_form)
        session_form = json.loads(form_elems.session_form)
        event = DataGetter.get_event(event_id)
        if request.method == 'POST':
            speaker_img_file = ""
            slide_file = ""
            video_file = ""
            audio_file = ""
            if 'slides' in request.files and request.files['slides'].filename != '':
                slide_file = request.files['slides']
            if 'video' in request.files and request.files['video'].filename != '':
                video_file = request.files['video']
            if 'audio' in request.files and request.files['audio'].filename != '':
                audio_file = request.files['audio']
            if 'photo' in request.files and request.files['photo'].filename != '':
                speaker_img_file = request.files['photo']
            DataManager.edit_session(request.form, session, event_id, speaker_img_file,
                                     slide_file, audio_file, video_file)
            return redirect(url_for('.index_view', event_id=event_id))
        if request.method == 'GET':
            return self.render('/gentelella/admin/event/sessions/edit.html', session=session,
                               speaker_form=speaker_form, session_form=session_form, event=event)

    @expose('/<int:session_id>/accept', methods=('GET',))
    @can_accept_and_reject
    def accept_session(self, event_id, session_id):
        session = get_session_or_throw(session_id)
        session.state = 'accepted'
        save_to_db(session, 'Session Accepted')
        flash("The session has been accepted")
        return redirect(url_for('.index_view', event_id=event_id))

    @expose('/<int:session_id>/reject', methods=('GET',))
    @can_accept_and_reject
    def reject_session(self, event_id, session_id):
        session = get_session_or_throw(session_id)
        session.state = 'rejected'
        save_to_db(session, 'Session Rejected')
        flash("The session has been rejected")
        return redirect(url_for('.index_view', event_id=event_id))

    @expose('/<int:session_id>/delete', methods=('GET',))
    def delete_session(self, event_id, session_id):
        session = get_session_or_throw(session_id)
        delete_from_db(session, 'Session Rejected')
        flash("The session has been deleted", "danger")
        return redirect(url_for('.index_view', event_id=event_id))
