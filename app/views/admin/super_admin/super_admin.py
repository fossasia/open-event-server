from flask_admin import expose

from app.views.admin.super_admin.super_admin_base import SuperAdminBaseView
from ....helpers.data_getter import DataGetter
from app.helpers.helpers import get_latest_heroku_release, get_commit_info


class SuperAdminView(SuperAdminBaseView):

    @expose('/')
    def index_view(self):
        events = DataGetter.get_all_events()[:5]
        number_live_events = DataGetter.get_all_live_events().count()
        number_draft_events = DataGetter.get_all_draft_events().count()
        number_past_events = DataGetter.get_all_past_events().count()
        super_admins = DataGetter.get_all_super_admins()
        admins = DataGetter.get_all_admins()
        registered_users = DataGetter.get_all_registered_users()
        organizers = DataGetter.get_all_organizers()
        co_organizers = DataGetter.get_all_co_organizers()
        track_organizers = DataGetter.get_all_track_organizers()
        attendees= DataGetter.get_all_attendees()
        version = get_latest_heroku_release()
        commit_number = None
        commit_info = None
        if version:
            commit_number = version['description'].split(' ')[1]
            commit_info = get_commit_info(commit_number)
        return self.render('/gentelella/admin/super_admin/widgets/index.html',
                           events=events,
                           version=version,
                           commit_info=commit_info,
                           number_live_events=number_live_events,
                           number_draft_events=number_draft_events,
                           number_past_events=number_past_events,
                           super_admins=super_admins,
                           admins=admins,
                           registered_users=registered_users,
                           organizers=organizers,
                           co_organizers=co_organizers,
                           track_organizers=track_organizers,
                           attendees=attendees)
