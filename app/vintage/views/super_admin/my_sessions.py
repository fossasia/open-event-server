import flask_login
from flask import Blueprint
from flask import render_template

from app.helpers.data_getter import DataGetter
from app.views.super_admin import check_accessible, SESSIONS, list_navbar
from app.views.super_admin.content import sadmin_content

sadmin_sessions = Blueprint('sadmin_sessions', __name__, url_prefix='/admin/sessions')


@sadmin_content.before_request
def verify_accessible():
    return check_accessible(SESSIONS)


@sadmin_sessions.route('/')
@flask_login.login_required
def display_my_sessions_view():
    all_sessions = DataGetter.get_all_sessions()
    all_pending = DataGetter.get_sessions_by_state('pending')
    all_accepted = DataGetter.get_sessions_by_state('accepted')
    all_rejected = DataGetter.get_sessions_by_state('rejected')
    all_trashed = DataGetter.get_trash_sessions()
    page_content = {"title": "Sessions Proposals"}
    return render_template('gentelella/super_admin/sessions/sessions.html',
                           page_content=page_content,
                           all_sessions=all_sessions,
                           all_pending=all_pending,
                           all_accepted=all_accepted,
                           all_rejected=all_rejected,
                           all_trashed=all_trashed,
                           navigation_bar=list_navbar())
