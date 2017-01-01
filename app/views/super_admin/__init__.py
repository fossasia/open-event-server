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

NAVIGATION_BAR = {
    'admin': ('/admin/', 'home', 'Admin', 'Dashboard'),
    'events': ('/admin/events/', 'events', 'Events', 'Manage All Events'),
    'sales': ('/admin/sales/', 'sales', 'Sales', 'View all Sales'),
    'sessions': ('/admin/sessions/', 'sessions', 'Sessions', 'Manage All Sessions'),
    'users': ('/admin/users/', 'users', 'Users', 'Users'),
    'permissions': ('/admin/permissions/', 'permissions', 'Permissions', 'Permissions'),
    'messages': ('/admin/messages/', 'messages', 'Messages', 'System Messages'),
    'reports': ('/admin/reports/', 'reports', 'Reports', 'Reports'),
    'settings': ('/admin/settings/', 'settings', 'Settings', 'Settings'),
    'modules': ('/admin/modules/', 'modules', 'Modules', 'Modules'),
    'content': ('/admin/content/', 'content', 'Content', 'Content')
}


def check_accessible(panel_name):
    if not AuthManager.is_accessible():
        return redirect(url_for('admin.login_view', next=request.url))
    else:
        if not current_user.can_access_panel(panel_name) and not current_user.is_staff:
            abort(403)


def list_navbar():
    navigation_bar = []
    for panel_name in PANEL_LIST:
        if current_user.can_access_panel(panel_name) or current_user.is_staff:
            navigation_bar.append(NAVIGATION_BAR[panel_name])

    return navigation_bar

