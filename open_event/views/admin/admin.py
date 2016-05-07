"""Copyright 2015 Rafal Kowalski"""
from flask.ext import login
from flask_admin import Admin

from open_event.models import db
from open_event.models.event import Event
from open_event.models.track import Track
from open_event.models.user import User
from open_event.views.admin.models_views.event import EventView
from open_event.views.admin.home import MyHomeView
from open_event.views.admin.track_view import TrackView

class AdminView(object):
    """Main Admin class View"""
    def __init__(self, app_name):
        self.admin = Admin(name=app_name, template_mode='bootstrap3', index_view=MyHomeView())

    def init(self, app):
        """Init flask admin"""
        self.admin.init_app(app)
        self._add_views()

    def _add_views(self):
        self._add_models_to_menu()

    def _add_models_to_menu(self):
        ev = EventView(Event, db.session)
        self.admin.add_view(ev)
        self.admin.add_view(TrackView(Track, db.session, name='Track', url='event/<event_id>/track'))

    @staticmethod
    def init_login(app):
        """Init login"""
        login_manager = login.LoginManager()
        login_manager.init_app(app)

        # Create user loader function
        @login_manager.user_loader
        def load_user(user_id):
            return db.session.query(User).get(user_id)
