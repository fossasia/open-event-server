"""Written by - Rafal Kowalski"""
from flask.ext.admin import BaseView, expose
from ....models.event import Event

class ApiView(BaseView):
    @expose('/')
    def index(self):
        events = Event.query.all()
        return self.render('admin/api/index.html', events=events)
