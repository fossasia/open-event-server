from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from flask.ext import login
from flask import request, url_for, redirect
from ....helpers.data import DataManager, save_to_db
from open_event.helpers.permission_decorators import is_coorganizer
from ....helpers.data_getter import DataGetter
import json


class SessionView(ModelView):

    def is_accessible(self):
        return login.current_user.is_authenticated

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('admin.login_view', next=request.url))

    @expose('/')
    def index_view(self, event_id):
        sessions = DataGetter.get_sessions_by_event_id(event_id)
        event = DataGetter.get_event(event_id)
        return self.render('/gentelella/admin/event/session/display.html',
                           sessions=sessions, event_id=event_id, event=event)

    @expose('/display/')
    def display_view(self, event_id):
        sessions = DataGetter.get_sessions_by_event_id(event_id)
        event = DataGetter.get_event(event_id)
        return self.render('/gentelella/admin/event/session/display.html',
                           sessions=sessions, event_id=event_id, event=event)

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
            return redirect(url_for('session.index_view', event_id=event_id))
        return self.render('/gentelella/admin/event/session/new/new.html',
                           speaker_form=speaker_form, session_form=session_form)

    @expose('/new/<user_id>/<hash>/', methods=('GET', 'POST'))
    def new_view(self, event_id, user_id, hash):
        invite = DataGetter.get_invite_by_user_id(user_id)
        if invite and invite.hash == hash:
            if request.method == 'POST':
                DataManager.add_session_to_event(request.form, event_id)
                return redirect(url_for('session.index_view', event_id=event_id))
            return self.render('/gentelella/admin/session/new/new.html')

    @expose('/<int:session_id>/invited/', methods=('GET', 'POST'))
    def invited_view(self, event_id, session_id):
        session = DataGetter.get_session(session_id)

        return self.render('/gentelella/admin/event/session/invited.html',
                           session=session, event_id=event_id)

    @expose('/<int:session_id>/speaker/', methods=('GET', 'POST'))
    def speaker_view(self, event_id, session_id):
        session = DataGetter.get_session(session_id)
        form_elems = DataGetter.get_custom_form_elements(event_id)
        if request.method == 'POST':
            DataManager.add_speaker_to_session(request.form, event_id, session_id)
            return redirect(url_for('session.index_view', event_id=event_id))
        return self.render('/gentelella/admin/event/session/speaker.html',
                           session=session, event_id=event_id, form_elems=form_elems)

    @expose('/<int:session_id>/edit/', methods=('GET', 'POST'))
    def edit_view(self, event_id, session_id):
        session = DataGetter.get_session(session_id)
        if request.method == 'GET':
            return self.render('/gentelella/admin/session/edit.html', session=session)
        if request.method == 'POST':
            DataManager.edit_session(request.form, session)
            return redirect(url_for('session.index_view', event_id=event_id))

    @expose('/<int:session_id>/accept_session', methods=('GET',))
    def accept_session(self, event_id, session_id):
        session = DataGetter.get_session(session_id)
        session.state = 'accepted'
        save_to_db(session, 'Session Accepted')
        return redirect(url_for('.display_view', event_id=event_id))

    @expose('/<int:session_id>/reject_session', methods=('GET',))
    def reject_session(self, event_id, session_id):
        session = DataGetter.get_session(session_id)
        session.state = 'rejected'
        save_to_db(session, 'Session Rejected')
        return redirect(url_for('.display_view', event_id=event_id))

    @expose('/mysessions/', methods=('GET', 'POST'))
    def user_sessions_view(self, event_id):
        pass


