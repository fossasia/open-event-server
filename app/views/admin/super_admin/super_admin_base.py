from flask import request, url_for, redirect
from flask.ext.restplus import abort
from flask_admin import BaseView
from flask.ext.login import current_user

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
    SESSIONS,
    USERS,
    PERMISSIONS,
    REPORTS,
    SETTINGS,
    MESSAGES,
    MODULES,
    CONTENT,
    SALES,
]

class SuperAdminBaseView(BaseView):
    PANEL_NAME = BASE

    def is_accessible(self):
        return current_user.is_authenticated

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('admin.login_view', next=request.url))
        else:
            if not current_user.can_access_panel(self.PANEL_NAME) or not current_user.is_staff:
                abort(403)
