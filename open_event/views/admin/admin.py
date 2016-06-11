"""Copyright 2015 Rafal Kowalski"""
from flask.ext import login
from flask_admin import Admin

from open_event.models import db
from open_event.models.event import Event
from open_event.models.role import Role
from open_event.models.user import User
from open_event.models.track import Track
from open_event.models.invite import Invite
from open_event.models.session import Session
from open_event.models.speaker import Speaker
from open_event.models.sponsor import Sponsor
from open_event.views.admin.models_views.events import EventsView
from open_event.views.admin.models_views.my_sessions import MySessionView
from open_event.views.admin.models_views.roles import RoleView
from open_event.views.admin.models_views.profile import ProfileView
from open_event.views.admin.models_views.scheduler import SchedulerView
from open_event.views.admin.models_views.tracks import TracksView
from open_event.views.admin.models_views.invite import InviteView
from open_event.views.admin.models_views.session import SessionView
from open_event.views.admin.models_views.events_speakers import EventsSpeakersView
from open_event.views.admin.models_views.events_sponsors import EventsSponsorsView
from open_event.views.admin.home import MyHomeView


class AdminView(object):
    """Main Admin class View"""
    def __init__(self, app_name):
        self.admin = Admin(name=app_name, template_mode='bootstrap3', index_view=MyHomeView())

    def init(self, app):
        """Init flask admin"""
        self.admin.init_app(app)
        self._add_views()

    def _add_views(self):
        self.admin.add_view(EventsView(Event, db.session, name='Events', url='events'))
        self.admin.add_view(MySessionView(name='MySessions', url='events/mysessions'))
        self.admin.add_view(EventsSpeakersView(Speaker, db.session, name='Speaker', url='events/<event_id>/speakers'))
        self.admin.add_view(EventsSponsorsView(Sponsor, db.session, name='Sponsor', url='events/<event_id>/sponsors'))
        self.admin.add_view(SessionView(Session, db.session, name='Sessions', url='events/<event_id>/sessions'))
        self.admin.add_view(SchedulerView(name='Scheduler', url='events/<event_id>/scheduler'))
        self.admin.add_view(RoleView(Role, db.session, name='Role', url='events/<event_id>/roles'))
        self.admin.add_view(ProfileView(User, db.session, name='Profile', url='profile'))
        self.admin.add_view(TracksView(Track, db.session, name='Track', url='events/<event_id>/tracks'))
        self.admin.add_view(InviteView(Invite, db.session, name='Invite', url='events/<event_id>/invite'))

    @staticmethod
    def init_login(app):
        """Init login"""
        login_manager = login.LoginManager()
        login_manager.init_app(app)

        # Create user loader function
        @login_manager.user_loader
        def load_user(user_id):
            return db.session.query(User).get(user_id)

