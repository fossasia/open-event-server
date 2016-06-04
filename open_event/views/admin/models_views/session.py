from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from flask import request, url_for, redirect
from ....helpers.data import DataManager,save_to_db
from ....helpers.data_getter import DataGetter


class SessionView(ModelView):

    @expose('/new/<user_id>/<hash>/', methods=('GET', 'POST'))
    def create_view(self, event_id, user_id, hash):
        invite = DataGetter.get_invite_by_user_id(user_id)
        if invite and invite.hash == hash:
            if request.method == 'POST':
                DataManager.add_session_to_event(request.form, event_id)
                return redirect(url_for('session.display_view', event_id=event_id))
            return self.render('/gentelella/admin/session/new.html')

    @expose('/display/')
    def display_view(self, event_id):
        sessions = DataGetter.get_sessions_by_event_id(event_id)
        return self.render('/gentelella/admin/session/display.html',
                           sessions=sessions)

    @expose('/<int:session_id>/accept_session', methods=('GET', 'POST'))
    def accept_session(self, event_id, session_id):
        session = DataGetter.get_session(session_id)
        session.state = 'accepted'
        save_to_db(session, 'Session Accepted')
        return redirect(url_for('.display_view', event_id=event_id))

    @expose('/<int:session_id>/reject_session', methods=('GET', 'POST'))
    def reject_session(self, event_id, session_id):
        session = DataGetter.get_session(session_id)
        session.state = 'rejected'
        save_to_db(session, 'Session Rejected')
        return redirect(url_for('.display_view', event_id=event_id))
