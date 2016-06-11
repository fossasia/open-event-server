from flask_admin import BaseView, expose
from ....helpers.data_getter import DataGetter

class MySessionView(BaseView):
    @expose('/')
    def display_my_sessions_view(self):
        upcoming_events_sessions = DataGetter.get_sessions_of_user(upcoming_events=True)
        past_events_sessions = DataGetter.get_sessions_of_user(upcoming_events=False)
        # browse(locals())
        return self.render('/gentelella/admin/mysessions/mysessions_list.html',
                           upcoming_events_sessions=upcoming_events_sessions, past_events_sessions=past_events_sessions)

    @expose('/<session_id>')
    def display_session_view(self, session_id):
        session = DataGetter.get_session(session_id)
        return self.render('/gentelella/admin/mysessions/mysession_detail.html', session=session)
