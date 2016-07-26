from flask.ext.admin import BaseView
from flask_admin import expose

from app import db
from app.helpers.permission_decorators import *
from flask.ext import login
from flask import request, url_for, redirect, flash
from ....helpers.data import DataManager, delete_from_db, trash_session, restore_session
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
        if not event.has_session_speakers:
            return self.render('/gentelella/admin/event/info/enable_module.html', active_page='sessions',
                               title='Sessions', event=event)
        return self.render('/gentelella/admin/event/sessions/base_session_table.html',
                           sessions=sessions, event_id=event_id, event=event)

    @expose('/<int:session_id>/', methods=('GET', 'POST'))
    def session_display_view(self, event_id, session_id):
        session = get_session_or_throw(session_id)
        if request.method == 'POST':
            DataManager.edit_session(request, session)
            return redirect(url_for('.index_view', event_id=event_id))
        event = DataGetter.get_event(event_id)
        if not event.has_session_speakers:
            return self.render('/gentelella/admin/event/info/enable_module.html', active_page='sessions',
                               title='Sessions', event=event)
        form_elems = DataGetter.get_custom_form_elements(event_id)
        if not form_elems:
            flash("Speaker and Session forms have been incorrectly configured for this event."
                  " Session creation has been disabled", "danger")
            return redirect(url_for('.index_view', event_id=event_id))
        session_form = json.loads(form_elems.session_form)
        speakers = DataGetter.get_speakers(event_id).all()

        return self.render('/gentelella/admin/event/sessions/edit.html',
                           session=session, session_form=session_form, event_id=event_id,
                           event=event, speakers=speakers)

    @expose('/create/', methods=('GET', 'POST'))
    @can_access
    def create_view(self, event_id):
        event = DataGetter.get_event(event_id)
        if not event.has_session_speakers:
            return self.render('/gentelella/admin/event/info/enable_module.html', active_page='sessions',
                               title='Sessions', event=event)
        if request.method == 'POST':
            DataManager.add_session_to_event(request, event_id)
            flash("The session and speaker have been saved")
            get_from = request.args.get("from")
            if get_from and get_from == 'speaker':
                return redirect(url_for('event_speakers.index_view', event_id=event_id))
            return redirect(url_for('.index_view', event_id=event_id))

        form_elems = DataGetter.get_custom_form_elements(event_id)
        if not form_elems:
            flash("Speaker and Session forms have been incorrectly configured for this event."
                  " Session creation has been disabled", "danger")
            return redirect(url_for('.index_view', event_id=event_id))
        speaker_form = json.loads(form_elems.speaker_form)
        session_form = json.loads(form_elems.session_form)
        speakers = DataGetter.get_speakers(event_id).all()

        return self.render('/gentelella/admin/event/sessions/new.html',
                           speaker_form=speaker_form, session_form=session_form, event=event, speakers=speakers)

    @expose('/<int:session_id>/edit/', methods=('GET', 'POST'))
    @can_access
    def edit_view(self, event_id, session_id):

        event = DataGetter.get_event(event_id)
        if not event.has_session_speakers:
            return self.render('/gentelella/admin/event/info/enable_module.html', active_page='sessions',
                               title='Sessions', event=event)

        session = get_session_or_throw(session_id)
        if request.method == 'POST':
            DataManager.edit_session(request, session)
            return redirect(url_for('.index_view', event_id=event_id))

        form_elems = DataGetter.get_custom_form_elements(event_id)
        if not form_elems:
            flash("Speaker and Session forms have been incorrectly configured for this event."
                  " Session creation has been disabled", "danger")
            return redirect(url_for('.index_view', event_id=event_id))
        session_form = json.loads(form_elems.session_form)
        speakers = DataGetter.get_speakers(event_id).all()
        return self.render('/gentelella/admin/event/sessions/edit.html', session=session,
                           session_form=session_form, event=event, speakers=speakers)

    @expose('/new/<user_id>/<hash>/', methods=('GET', 'POST'))
    def new_view(self, event_id, user_id, hash):
        invite = DataGetter.get_invite_by_user_id(user_id)
        event = DataGetter.get_event(event_id)
        if invite and invite.hash == hash:
            if request.method == 'POST':
                DataManager.add_session_to_event(request, event_id)
                return redirect(url_for('.index_view', event_id=event_id))
            return self.render('/gentelella/admin/sessions/new.html', event=event)

    @expose('/<int:session_id>/invited/', methods=('GET', 'POST'))
    def invited_view(self, event_id, session_id):
        session = DataGetter.get_session(session_id)
        event = DataGetter.get_event(event_id)
        return self.render('/gentelella/admin/event/sessions/invited.html',
                           session=session, event_id=event_id, event=event)

    @expose('/<int:session_id>/add_speaker/', methods=('GET', 'POST'))
    def add_speaker_view(self, event_id, session_id):
        session = DataGetter.get_session(session_id)
        event = DataGetter.get_event(event_id)
        if not event.has_session_speakers:
            return self.render('/gentelella/admin/event/info/enable_module.html', active_page='sessions',
                               title='Sessions', event=event)
        form_elems = DataGetter.get_custom_form_elements(event_id)
        if not form_elems:
            flash("Speaker form has been incorrectly configured for this event. Editing has been disabled", "danger")
            return redirect(url_for('.index_view', event_id=event_id))
        speaker_form = json.loads(form_elems.speaker_form)
        if request.method == 'GET':
            return self.render('/gentelella/admin/event/speakers/edit.html', event_id=event_id,
                               event=event, speaker_form=speaker_form)
        if request.method == 'POST':
            DataManager.add_speaker_to_session(request, event_id, session_id)
            flash("The speaker has been added to session")
            return redirect(url_for('.index_view', event_id=event_id))

    @expose('/<int:session_id>/accept', methods=('GET',))
    @can_accept_and_reject
    def accept_session(self, event_id, session_id):
        session = get_session_or_throw(session_id)
        DataManager.session_accept_reject(session, event_id, 'accepted')
        return redirect(url_for('.index_view', event_id=event_id))

    @expose('/<int:session_id>/reject', methods=('GET',))
    @can_accept_and_reject
    def reject_session(self, event_id, session_id):
        session = get_session_or_throw(session_id)
        DataManager.session_accept_reject(session, event_id, 'rejected')
        return redirect(url_for('.index_view', event_id=event_id))

    @expose('/<int:session_id>/trash', methods=('GET',))
    def trash_session(self, event_id, session_id):
        session = get_session_or_throw(session_id)
        session = trash_session(session_id)
        flash("The session has been deleted", "danger")
        if login.current_user.is_super_admin:
            return redirect(url_for('sadmin_sessions.display_my_sessions_view', event_id=event_id))
        return redirect(url_for('.index_view', event_id=event_id))

    @expose('/<int:session_id>/restore_trash', methods=('GET',))
    def restore_session(self, event_id, session_id):
        restore_session(session_id)
        flash("The session has been restored", "success")
        return redirect(url_for('sadmin_sessions.display_my_sessions_view', event_id=event_id))

    @expose('/<int:session_id>/delete', methods=('GET',))
    def delete_session(self, event_id, session_id):
        session = get_session_or_throw(session_id)
        delete_from_db(session, 'Session Deleted')
        flash("The session has been permanently deleted", "danger")
        return redirect(url_for('sadmin_sessions.display_my_sessions_view', event_id=event_id))

    @expose('/<int:session_id>/restore/', methods=('GET',))
    def restore_session_view(self, event_id, session_id):
        session = get_session_or_throw(session_id)
        event = DataGetter.get_event(event_id)
        return self.render('/gentelella/admin/event/sessions/browse_revisions.html',
                           session=session, event_id=event_id, event=event)

    @expose('/<int:session_id>/restore/<int:version_id>', methods=('GET',))
    def restore_session_revision(self, event_id, session_id, version_id):
        session = get_session_or_throw(session_id)
        version = session.versions[version_id]
        version.revert()
        db.session.commit()
        flash("The session has been restored.", "success")
        return redirect(url_for('.index_view', event_id=event_id))

