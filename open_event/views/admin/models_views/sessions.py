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
            speaker_img_filename = ""
            if 'slides' in request.files:
                slide_file = request.files['slides']
                slide_filename = secure_filename(slide_file.filename)
                slide_file.save(os.path.join(os.path.realpath('.') + '/static/media/image/', slide_filename))
            if 'photo' in request.files:
                speaker_img_file = request.files['photo']
                speaker_img_filename = secure_filename(speaker_img_file.filename)
                speaker_img_file.save(os.path.join(os.path.realpath('.') + '/static/media/image/', speaker_img_filename))
            DataManager.add_session_to_event(request.form, event_id, speaker_img_filename)
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
        if request.method == 'GET':
            return self.render('/gentelella/admin/sessions/edit.html', session=session)
        if request.method == 'POST':
            DataManager.edit_session(request.form, session)
            return redirect(url_for('.index_view', event_id=event_id))

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
