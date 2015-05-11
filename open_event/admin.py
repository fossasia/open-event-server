from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib.sqla import ModelView
from models import Sponsor, Event, Speaker, Session, db


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
