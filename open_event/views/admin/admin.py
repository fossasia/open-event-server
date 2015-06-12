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

class AdminView(object):

    def __init__(self, app, app_name):
        self.app = app
        self.admin = Admin(name=app_name, template_mode='bootstrap3')

    def init(self):
        self.admin.init_app(self.app)
        self._add_views()

    def _add_views(self):
        self._add_models_to_menu()
        self.admin.add_view(ApiView(name='Api'))
        self._add_events_to_submenu()
        # self.admin.add_view(SuperView())

    def _add_events_to_submenu(self):
        for event in Event.query.all():
            self.admin.add_link(MenuLink(name=event.name, url='/admin/event/%s' % event.id, category="Switch event"))

    def _add_models_to_menu(self):
        event = Event.query.first()
        self.admin.add_view(EventView(Event, db.session))
        # if event:
        #     self.admin.add_view(SponsorView(Sponsor, db.session, endpoint="event/%s/sponsor" % event.id))
        #     self.admin.add_view(SpeakerView(Speaker, db.session, endpoint="event/%s/speaker" % event.id))
        #     self.admin.add_view(SessionView(Session, db.session, endpoint="event/%s/session" % event.id))
        #     self.admin.add_view(TrackView(Track, db.session, endpoint="event/%s/track" % event.id))
        #     self.admin.add_view(MicrolocationView(Microlocation, db.session, endpoint="event/%s/microlocation" % event.id))
