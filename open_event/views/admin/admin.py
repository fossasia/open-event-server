from flask.ext.admin import Admin, expose
from flask.ext.admin.contrib.sqla import ModelView

from open_event.models import db
from open_event.models.session import Session
from open_event.models.track import Track
from open_event.models.speaker import Speaker
from open_event.models.sponsor import Sponsor
from open_event.models.microlocation import Microlocation
from open_event.models.event import Event
from open_event.views.admin.config import ConfigView


class AdminView(object):

    def __init__(self, app, app_name):
        self.app = app
        self.admin = Admin(name=app_name)

    def init(self):
        self.admin.init_app(self.app)
        self._add_views()

    def _add_views(self):
        self.admin.add_view(ModelView(Event, db.session))
        self.admin.add_view(ModelView(Sponsor, db.session))
        self.admin.add_view(ModelView(Speaker, db.session))
        self.admin.add_view(ModelView(Session, db.session))
        self.admin.add_view(ModelView(Track, db.session))
        self.admin.add_view(ModelView(Microlocation, db.session))
        self.admin.add_view(ConfigView(name='Settings'))