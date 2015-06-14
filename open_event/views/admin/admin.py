"""Written by - Rafal Kowalski"""
from flask.ext.admin import Admin
from open_event.models import db
from open_event.models.event import Event
from open_event.views.admin.models_views.event import EventView
from open_event.views.admin.models_views.api import ApiView
from flask.ext.admin.base import AdminIndexView
from flask.ext.admin import expose


class MyHomeView(AdminIndexView):
    @expose('/')
    def index(self):
        events = Event.query.all()
        return self.render('admin/base1.html', events=events)


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
        self.admin.add_view(ApiView(name='Api'))
