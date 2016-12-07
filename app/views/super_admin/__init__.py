from flask import request, url_for, redirect
from flask.ext.login import current_user
from flask.ext.restplus import abort
from app.helpers.auth import AuthManager

# Admin Panels
BASE = 'admin'
EVENTS = 'events'
SESSIONS = 'sessions'
USERS = 'users'
PERMISSIONS = 'permissions'
REPORTS = 'reports'
SETTINGS = 'settings'
MESSAGES = 'messages'
MODULES = 'modules'
CONTENT = 'content'
SALES = 'sales'

PANEL_LIST = [
    BASE,
    EVENTS,
    SALES,
    SESSIONS,
    USERS,
    PERMISSIONS,
    MESSAGES,
    REPORTS,
    SETTINGS,
    MODULES,
    CONTENT,
]


def check_accessible(panel_name):
    if not AuthManager.is_accessible():
        return redirect(url_for('admin.login_view', next=request.url))
    else:
        if not current_user.can_access_panel(panel_name) or not current_user.is_staff:
            abort(403)
