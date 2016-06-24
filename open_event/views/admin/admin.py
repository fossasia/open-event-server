"""Copyright 2015 Rafal Kowalski"""
from flask.ext import login
from flask_admin import Admin

from open_event.models import db
from open_event.models.user import User
from open_event.views.admin.models_views.events import EventsView
from open_event.views.admin.models_views.my_sessions import MySessionView
from open_event.views.admin.models_views.roles import RoleView
from open_event.views.admin.models_views.profile import ProfileView
from open_event.views.admin.models_views.settings import SettingsView
from open_event.views.admin.models_views.scheduler import SchedulerView
from open_event.views.admin.models_views.invite import InviteView
from open_event.views.admin.models_views.sessions import SessionsView
from open_event.views.admin.models_views.speakers import SpeakersView
from open_event.views.admin.home import MyHomeView
from open_event.views.public.event_detail import EventDetailView
from open_event.views.public.browse import BrowseView
from open_event.views.public.pages import BasicPagesView
from open_event.views.admin.super_admin.super_admin import SuperAdminView
from open_event.views.admin.super_admin.events import SuperAdminEventsView
from open_event.views.admin.super_admin.my_sessions import SuperAdminMySessionView
from open_event.views.admin.super_admin.users import SuperAdminUsersView
from open_event.views.admin.super_admin.permissions import SuperAdminPermissionsView
from open_event.views.admin.super_admin.reports import SuperAdminReportsView
from open_event.views.admin.super_admin.logs import SuperAdminLogsView
from open_event.views.admin.super_admin.dep_settings import SuperAdminSettingsView


class AdminView(object):
    """Main Admin class View"""

    def __init__(self, app_name):
        self.admin = Admin(name=app_name, template_mode='bootstrap3', index_view=MyHomeView(
            name='Home',
            url='/'
        ), static_url_path='/static')

    def init(self, app):
        """Init flask admin"""
        self.admin.init_app(app)
        self._add_views()

    def _add_views(self):

        self.admin.add_view(EventDetailView(name='Event Detail', url='/e', endpoint="event_detail"))
        self.admin.add_view(BrowseView(name='Search Results', url='/<location>/events', endpoint="search_results"))
        self.admin.add_view(BasicPagesView(name='Page', url='/'))
        self.admin.add_view(MySessionView(name='MySessions', url='/events/mysessions', endpoint="my_sessions"))
        self.admin.add_view(EventsView(name='Events', url='/events', endpoint="events"))
        self.admin.add_view(SpeakersView(name='Speakers', url='/events/<event_id>/speakers', endpoint="event_speakers"))
        self.admin.add_view(SessionsView(name='Sessions', url='/events/<event_id>/sessions', endpoint="event_sessions"))
        self.admin.add_view(SchedulerView(name='Scheduler', url='/events/<event_id>/scheduler', endpoint="event_scheduler"))
        self.admin.add_view(RoleView(name='Role', url='/events/<event_id>/roles', endpoint="event_roles"))
        self.admin.add_view(ProfileView(name='Profile', url='/profile', endpoint="profile"))
        self.admin.add_view(InviteView(name='Invite', url='/events/<event_id>/invite', endpoint="event_invites"))
        self.admin.add_view(SettingsView(name='Settings', url='/settings', endpoint="settings"))

        self.admin.add_view(SuperAdminView(name='Admin', url='/admin/', endpoint="sadmin"))
        self.admin.add_view(SuperAdminEventsView(name='Events', url='/admin/events', endpoint="sadmin_events"))
        self.admin.add_view(SuperAdminMySessionView(name='Sessions', url='/admin/sessions', endpoint="sadmin_sessions"))
        self.admin.add_view(SuperAdminUsersView(name='Users', url='/admin/users', endpoint="sadmin_users"))
        self.admin.add_view(SuperAdminPermissionsView(name='Permissions', url='/admin/permissions', endpoint="sadmin_permissions"))
        self.admin.add_view(SuperAdminReportsView(name='Reports', url='/admin/reports', endpoint="sadmin_reports"))
        self.admin.add_view(SuperAdminLogsView(name='Logs', url='/admin/logs', endpoint="sadmin_logs"))
        self.admin.add_view(SuperAdminSettingsView(name='Settings', url='/admin/settings', endpoint="sadmin_settings"))

    @staticmethod
    def init_login(app):
        from flask import request, url_for, redirect
        """Init login"""
        login_manager = login.LoginManager()
        login_manager.init_app(app)

        # Create user loader function
        @login_manager.user_loader
        def load_user(user_id):
            return db.session.query(User).get(user_id)

        @login_manager.unauthorized_handler
        def unauthorized():
            return redirect(url_for('admin.login_view', next=request.url))
