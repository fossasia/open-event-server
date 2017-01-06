from flask import request
from flask import url_for
from werkzeug.utils import redirect

from app.helpers.auth import AuthManager
from app.views.home import home_routes
from app.views.public.babel_view import babel
from app.views.public.event_detail import event_detail
from app.views.public.event_invoice import event_invoicing
from app.views.public.explore import explore
from app.views.public.pages import pages
from app.views.public.ticketing import ticketing
from app.views.sitemap import sitemaps
from app.views.super_admin.content import sadmin_content
from app.views.super_admin.debug import sadmin_debug
from app.views.super_admin.dep_settings import sadmin_settings
from app.views.super_admin.events import sadmin_events
from app.views.super_admin.messages import sadmin_messages
from app.views.super_admin.modules import sadmin_modules
from app.views.super_admin.my_sessions import sadmin_sessions
from app.views.super_admin.permissions import sadmin_permissions
from app.views.super_admin.reports import sadmin_reports
from app.views.super_admin.sales import sadmin_sales
from app.views.super_admin.super_admin import sadmin
from app.views.super_admin.users import sadmin_users
from app.views.users.events import events
from app.views.users.settings import settings
from app.views.users.export import event_export
from app.views.users.invite import event_invites
from app.views.users.my_sessions import my_sessions
from app.views.users.my_tickets import my_tickets
from app.views.users.notifications import notifications
from app.views.users.profile import profile
from app.views.users.roles import event_roles
from app.views.users.scheduler import event_scheduler
from app.views.users.sessions import event_sessions
from app.views.users.speakers import event_speakers
from app.views.users.ticket_sales import event_ticket_sales
from app.views.users.sponsors import event_sponsors
from app.views.utils_routes import utils_routes


class BlueprintsManager:
    def __init__(self):
        pass

    @staticmethod
    def register(app):
        """
        Register blueprints
        :param app: a flask app instance
        :return:
        """
        app.register_blueprint(pages)

        app.register_blueprint(home_routes)
        app.register_blueprint(utils_routes)
        app.register_blueprint(sitemaps)

        app.register_blueprint(babel)
        app.register_blueprint(event_invoicing)
        app.register_blueprint(explore)
        app.register_blueprint(ticketing)
        app.register_blueprint(event_detail)

        # Blueprints that require login
        app.register_blueprint(events)
        app.register_blueprint(event_speakers)
        app.register_blueprint(event_sessions)
        app.register_blueprint(event_scheduler)
        app.register_blueprint(event_export)
        app.register_blueprint(event_roles)
        app.register_blueprint(event_invites)
        app.register_blueprint(event_ticket_sales)
        app.register_blueprint(event_sponsors)

        app.register_blueprint(my_tickets)
        app.register_blueprint(my_sessions)
        app.register_blueprint(settings)
        app.register_blueprint(notifications)
        app.register_blueprint(profile)

        # Blueprints that are accessible only by a super admin
        app.register_blueprint(sadmin)
        app.register_blueprint(sadmin_events)
        app.register_blueprint(sadmin_sales)
        app.register_blueprint(sadmin_sessions)
        app.register_blueprint(sadmin_users)
        app.register_blueprint(sadmin_permissions)
        app.register_blueprint(sadmin_messages)
        app.register_blueprint(sadmin_reports)
        app.register_blueprint(sadmin_settings)
        app.register_blueprint(sadmin_modules)
        app.register_blueprint(sadmin_content)
        app.register_blueprint(sadmin_debug)


@event_speakers.before_request
@event_sessions.before_request
@event_scheduler.before_request
@event_export.before_request
@events.before_request
@event_roles.before_request
@event_sponsors.before_request
@event_invites.before_request
@event_ticket_sales.before_request
@my_tickets.before_request
@my_sessions.before_request
@settings.before_request
@notifications.before_request
@profile.before_request
def check_accessible():
    if not AuthManager.is_accessible():
        return redirect(url_for('admin.login_view', next=request.url))
