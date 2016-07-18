import json

import flask_login
from flask import flash, redirect, url_for, request
from flask.ext.restplus import abort
from flask_admin import BaseView, expose

from app.helpers.data import DataManager
from app.views.admin.models_views.events import is_verified_user
from ....helpers.data_getter import DataGetter

class MySessionView(BaseView):

    @expose('/')
    @flask_login.login_required
    def display_my_sessions_view(self):
        upcoming_events_sessions = DataGetter.get_sessions_of_user(upcoming_events=True)
        past_events_sessions = DataGetter.get_sessions_of_user(upcoming_events=False)
        page_content = {"tab_upcoming_events": "Upcoming Sessions",
                        "tab_past_events": "Past Sessions",
                        "title": "My Session Proposals"}
        if not is_verified_user():
            flash("Your account is unverified. "
                  "Please verify by clicking on the confirmation link that has been emailed to you.")
        return self.render('/gentelella/admin/mysessions/mysessions_list.html',
                           upcoming_events_sessions=upcoming_events_sessions, past_events_sessions=past_events_sessions,
                           page_content=page_content)

    @expose('/<int:session_id>/', methods=('GET',))
    @flask_login.login_required
    def display_session_view(self, session_id):
        session = DataGetter.get_sessions_of_user_by_id(session_id)
        if not session:
            abort(404)
        form_elems = DataGetter.get_custom_form_elements(session.event_id)
        if not form_elems:
            flash("Speaker and Session forms have been incorrectly configured for this event."
                  " Session creation has been disabled", "danger")
            return redirect(url_for('.display_my_sessions_view', event_id=session.event_id))
        speaker_form = json.loads(form_elems.speaker_form)
        session_form = json.loads(form_elems.session_form)
        event = DataGetter.get_event(session.event_id)
        speakers = DataGetter.get_speakers(session.event_id).all()
        return self.render('/gentelella/admin/mysessions/mysession_detail.html', session=session,
                           speaker_form=speaker_form, session_form=session_form, event=event, speakers=speakers)

    @expose('/<int:session_id>/', methods=('POST',))
    @flask_login.login_required
    def process_session_view(self, session_id):
        session = DataGetter.get_sessions_of_user_by_id(session_id)
        DataManager.edit_session(request, session)
        flash("The session has been updated successfully", "success")
        return redirect(url_for('.display_session_view', session_id=session_id))
