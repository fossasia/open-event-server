"""Copyright 2015 Rafal Kowalski"""
from flask.ext import login
from flask_admin import Admin

from app.models import db
from app.models.user import User
from app.views.admin.models_views.events import EventsView
from app.views.admin.models_views.my_tickets import MyTicketsView
from app.views.admin.models_views.my_sessions import MySessionView
from app.views.admin.models_views.export import ExportView
from app.views.admin.models_views.roles import RoleView
from app.views.admin.models_views.profile import ProfileView, NotificationView
from app.views.admin.models_views.settings import SettingsView
from app.views.admin.models_views.scheduler import SchedulerView
from app.views.admin.models_views.invite import InviteView
from app.views.admin.models_views.sessions import SessionsView
from app.views.admin.models_views.speakers import SpeakersView
from app.views.admin.home import MyHomeView
from app.views.admin.models_views.sponsors import SponsorsView
from app.views.admin.models_views.ticket_sales import TicketSalesView
from app.views.public.event_detail import EventDetailView
from app.views.public.explore import ExploreView
from app.views.public.pages import BasicPagesView
from app.views.admin.super_admin.super_admin import SuperAdminView
from app.views.admin.super_admin.events import SuperAdminEventsView
from app.views.admin.super_admin.my_sessions import SuperAdminMySessionView
from app.views.admin.super_admin.users import SuperAdminUsersView
from app.views.admin.super_admin.messages import SuperAdminMessagesView
from app.views.admin.super_admin.permissions import SuperAdminPermissionsView
from app.views.admin.super_admin.reports import SuperAdminReportsView
from app.views.admin.super_admin.logs import SuperAdminLogsView
from app.views.admin.super_admin.dep_settings import SuperAdminSettingsView
from app.views.admin.super_admin.modules import SuperAdminModulesView
from app.views.admin.super_admin.content import SuperAdminContentView
from app.views.public.ticketing import TicketingView

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

        # Public pages
        self.admin.add_view(BasicPagesView(name='Page', url='/'))
        self.admin.add_view(EventDetailView(name='Event Detail', url='/e', endpoint="event_detail"))
        self.admin.add_view(ExploreView(name='Explore', url='/explore', endpoint="explore"))
        self.admin.add_view(TicketingView(name='Ticketing & Orders', url='/orders', endpoint="ticketing"))

        # Accessible only after logging in

        self.admin.add_view(MyTicketsView(name='MyTicketsView', url='/mytickets', endpoint="my_tickets"))
        self.admin.add_view(MySessionView(name='MySessions', url='/events/mysessions', endpoint="my_sessions"))
        self.admin.add_view(EventsView(name='Events', url='/events', endpoint="events"))

        # Event level
        self.admin.add_view(SpeakersView(name='Speakers', url='/events/<int:event_id>/speakers', endpoint="event_speakers"))
        self.admin.add_view(SponsorsView(name='Sponsors', url='/events/<int:event_id>/sponsors', endpoint="event_sponsors"))
        self.admin.add_view(SessionsView(name='Sessions', url='/events/<int:event_id>/sessions', endpoint="event_sessions"))
        self.admin.add_view(SchedulerView(name='Scheduler', url='/events/<event_id>/scheduler',
                                          endpoint="event_scheduler"))
        self.admin.add_view(ExportView(name='Export', url='/events/<int:event_id>/export', endpoint="event_export"))
        self.admin.add_view(RoleView(name='Role', url='/events/<int:event_id>/roles', endpoint="event_roles"))
        self.admin.add_view(ProfileView(name='Profile', url='/profile', endpoint="profile"))
        self.admin.add_view(NotificationView(name='Notification', url='/notifications', endpoint='notifications'))
        self.admin.add_view(InviteView(name='Invite', url='/events/<int:event_id>/invite', endpoint="event_invites"))
        self.admin.add_view(TicketSalesView(name='Tickets', url='/events/<int:event_id>/tickets',
                                            endpoint="event_ticket_sales"))
        self.admin.add_view(SettingsView(name='Settings', url='/settings', endpoint="settings"))

        # Super Admin pages
        self.admin.add_view(SuperAdminView(name='Admin', url='/admin/', endpoint="sadmin"))
        self.admin.add_view(SuperAdminEventsView(name='Events', url='/admin/events', endpoint="sadmin_events"))
        self.admin.add_view(SuperAdminMySessionView(name='Sessions', url='/admin/sessions', endpoint="sadmin_sessions"))
        self.admin.add_view(SuperAdminUsersView(name='Users', url='/admin/users', endpoint="sadmin_users"))
        self.admin.add_view(SuperAdminPermissionsView(name='Permissions', url='/admin/permissions',
                                                      endpoint="sadmin_permissions"))
        self.admin.add_view(SuperAdminReportsView(name='Reports', url='/admin/reports', endpoint="sadmin_reports"))
        self.admin.add_view(SuperAdminLogsView(name='Logs', url='/admin/logs', endpoint="sadmin_logs"))
        self.admin.add_view(SuperAdminSettingsView(name='Settings', url='/admin/settings', endpoint="sadmin_settings"))
        self.admin.add_view(SuperAdminMessagesView(name='Messages', url='/admin/messages', endpoint="sadmin_messages"))
        self.admin.add_view(SuperAdminModulesView(name='Modules', url='/admin/modules', endpoint="sadmin_modules"))
        self.admin.add_view(SuperAdminContentView(name='Content', url='/admin/content', endpoint="sadmin_content"))

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
