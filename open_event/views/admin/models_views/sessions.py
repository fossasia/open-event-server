from flask.ext.admin import BaseView
from flask.ext.restplus import abort
from flask_admin import expose
from flask.ext import login
from flask import request, url_for, redirect, flash
from ....helpers.data import DataManager, save_to_db, delete_from_db
from ....helpers.data_getter import DataGetter
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
    def create_view(self, event_id):
        form_elems = DataGetter.get_custom_form_elements(event_id)
        speaker_form = ""
        session_form = ""
        for elem in form_elems:
            speaker_form = json.loads(elem.speaker_form)
            session_form = json.loads(elem.session_form)
        if request.method == 'POST':
            DataManager.add_session_to_event(request.form, event_id)
            return redirect(url_for('.index_view', event_id=event_id))
        return self.render('/gentelella/admin/event/sessions/new/new.html',
                           speaker_form=speaker_form, session_form=session_form)

    @expose('/new/<user_id>/<hash>/', methods=('GET', 'POST'))
    def new_view(self, event_id, user_id, hash):
        invite = DataGetter.get_invite_by_user_id(user_id)
        if invite and invite.hash == hash:
            if request.method == 'POST':
                DataManager.add_session_to_event(request.form, event_id)
                return redirect(url_for('.index_view', event_id=event_id))
            return self.render('/gentelella/admin/sessions/new/new.html')

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
    def edit_view(self, event_id, session_id):
        session = get_session_or_throw(session_id)
        if request.method == 'GET':
            return self.render('/gentelella/admin/sessions/edit.html', session=session)
        if request.method == 'POST':
            DataManager.edit_session(request.form, session)
            return redirect(url_for('.index_view', event_id=event_id))

    @expose('/<int:session_id>/accept', methods=('GET',))
    def accept_session(self, event_id, session_id):
        session = get_session_or_throw(session_id)
        session.state = 'accepted'
        save_to_db(session, 'Session Accepted')
        flash("The session has been accepted")
        return redirect(url_for('.index_view', event_id=event_id))

    @expose('/<int:session_id>/reject', methods=('GET',))
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
