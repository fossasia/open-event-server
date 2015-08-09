"""Copyright 2015 Rafal Kowalski"""
from flask_admin import BaseView, expose
from flask.ext import login
from ....helpers.data_getter import DataGetter

class ApiView(BaseView):
    @expose('/')
    def index(self):
        events = DataGetter.get_all_events()
        owner_events = DataGetter.get_all_owner_events(login.current_user.id)
        return self.render('admin/api/index.html', events=events, owner_events=owner_events)
