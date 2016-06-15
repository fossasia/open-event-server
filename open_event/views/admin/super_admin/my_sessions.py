import flask_login
from flask_admin import BaseView, expose
from ....helpers.data_getter import DataGetter


class SuperAdminMySessionView(BaseView):
    @expose('/')
    @flask_login.login_required
    def display_my_sessions_view(self):
        upcoming_events_sessions = DataGetter.get_sessions_of_user(upcoming_events=True)
        past_events_sessions = DataGetter.get_sessions_of_user(upcoming_events=False)
        return self.render('/gentelella/admin/mysessions/mysessions_list.html',
                           upcoming_events_sessions=upcoming_events_sessions,
                           past_events_sessions=past_events_sessions)
