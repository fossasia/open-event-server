"""Written by - Rafal Kowalski"""
from flask.ext.admin import Admin
from flask.ext.admin.base import MenuLink
from flask import url_for, render_template
from open_event.models import db
from open_event.models.session import Session
from open_event.models.track import Track
from open_event.models.speaker import Speaker
from open_event.models.sponsor import Sponsor
from open_event.models.microlocation import Microlocation
from open_event.models.event import Event

from open_event.views.admin.models_views.speaker import SpeakerView
from open_event.views.admin.models_views.event import EventView
from open_event.views.admin.models_views.sponsor import SponsorView
from open_event.views.admin.models_views.session import SessionView
# from open_event.views.admin.models_views.track import TrackView
from open_event.views.admin.models_views.microlocation import MicrolocationView
from open_event.views.admin.models_views.api import ApiView

from flask.ext.admin.base import AdminIndexView
from flask.ext.admin import expose


class MyHomeView(AdminIndexView):
    @expose('/')
    def index(self):
        events = Event.query.all()
        return self.render('admin/base.html', events=events)


class AdminView(object):

    def __init__(self, app, app_name):
        self.app = app
        self.admin = Admin(name=app_name, template_mode='bootstrap3', index_view=MyHomeView())

    def init(self):
        self.admin.init_app(self.app)
        self._add_views()

    def _add_views(self):
        self._add_models_to_menu()

    def _add_models_to_menu(self):
        self.admin.add_view(EventView(Event, db.session))
