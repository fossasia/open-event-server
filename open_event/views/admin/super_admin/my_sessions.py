import flask_login
from flask_admin import expose

from open_event.views.admin.super_admin.super_admin_base import SuperAdminBaseView
from ....helpers.data_getter import DataGetter


class SuperAdminMySessionView(SuperAdminBaseView):
    @expose('/')
    @flask_login.login_required
    def display_my_sessions_view(self):
        all_sessions = DataGetter.get_all_sessions()
        all_pending = DataGetter.get_sessions_by_state('pending')
        all_accepted = DataGetter.get_sessions_by_state('accepted')
        all_rejected = DataGetter.get_sessions_by_state('rejected')
        all_trashed = DataGetter.get_trash_sessions()
        page_content = {"title": "Sessions Proposals"}
        return self.render('/gentelella/admin/super_admin/sessions/sessions.html',
                           page_content=page_content,
                           all_sessions=all_sessions,
                           all_pending=all_pending,
                           all_accepted=all_accepted,
                           all_rejected=all_rejected,
                           all_trashed=all_trashed)
