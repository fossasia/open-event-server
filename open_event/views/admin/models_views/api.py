"""Copyright 2015 Rafal Kowalski"""
from flask_admin import BaseView, expose
from ....helpers.data_getter import DataGetter


class ApiView(BaseView):
    """Api View class"""
    @expose('/')
    def index(self):
        """Index view"""
        events = DataGetter.get_all_events()
        owner_events = DataGetter.get_all_owner_events()
        return self.render('admin/api/index.html', events=events, owner_events=owner_events)
