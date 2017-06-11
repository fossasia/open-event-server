import os

from flask import Blueprint, current_app as app
from flask import render_template

from app.helpers.data_getter import DataGetter
from app.helpers.deployment.kubernetes import KubernetesApi
from app.helpers.deployment.heroku import HerokuApi
from app.helpers.helpers import get_commit_info, get_count
from app.models.user import ATTENDEE, TRACK_ORGANIZER, COORGANIZER, ORGANIZER
from app.views.super_admin import BASE, check_accessible, list_navbar

sadmin = Blueprint('sadmin', __name__, url_prefix='/admin')


@sadmin.before_request
def verify_accessible():
    return check_accessible(BASE)


@sadmin.route('/')
def index_view():
    events = DataGetter.get_all_events()[:5]
    number_live_events = get_count(DataGetter.get_all_live_events())
    number_draft_events = get_count(DataGetter.get_all_draft_events())
    number_past_events = get_count(DataGetter.get_all_past_events())
    super_admins = DataGetter.get_all_super_admins()
    admins = DataGetter.get_all_admins()
    registered_users = DataGetter.get_all_registered_users()
    unverified_users = DataGetter.get_all_unverified_users()
    organizers = get_count(DataGetter.get_all_user_roles(ORGANIZER))
    co_organizers = get_count(DataGetter.get_all_user_roles(COORGANIZER))
    track_organizers = get_count(DataGetter.get_all_user_roles(TRACK_ORGANIZER))
    attendees = get_count(DataGetter.get_all_user_roles(ATTENDEE))
    accepted_sessions = get_count(DataGetter.get_all_accepted_sessions())
    rejected_sessions = get_count(DataGetter.get_all_rejected_sessions())
    draft_sessions = get_count(DataGetter.get_all_draft_sessions())
    email_times = DataGetter.get_email_by_times()


    commit_info = None
    heroku_release = None
    on_kubernetes = False
    pods_info = None
    repository = None
    commit_number = None
    branch = None
    on_heroku = False

    if KubernetesApi.is_on_kubernetes():
        on_kubernetes = True
        kubernetes_api = KubernetesApi()
        pods_info = kubernetes_api.get_pods()['items']
        repository = os.getenv('REPOSITORY', 'https://github.com/fossasia/open-event-orga-server.git')
        branch = os.getenv('BRANCH', 'development')
        commit_number = os.getenv('COMMIT_HASH', 'null')
        if commit_number != 'null':
            commit_info = get_commit_info(commit_number)
        else:
            commit_number = None
    elif HerokuApi.is_on_heroku():
        commit_info = None
        on_heroku = True
        heroku_api = HerokuApi()
        heroku_release = heroku_api.get_latest_release()
        if heroku_release:
            commit_number = heroku_release['description'].split(' ')[1]
            commit_info = get_commit_info(commit_number)

    return render_template('gentelella/super_admin/widgets/index.html',
                           events=events,
                           heroku_release=heroku_release,
                           commit_info=commit_info,
                           commit_number=commit_number,
                           on_heroku=on_heroku,
                           on_kubernetes=on_kubernetes,
                           version=app.config['VERSION'],
                           pods_info=pods_info,
                           number_live_events=number_live_events,
                           number_draft_events=number_draft_events,
                           number_past_events=number_past_events,
                           super_admins=super_admins,
                           admins=admins,
                           registered_users=registered_users,
                           unverified_users=unverified_users,
                           repository=repository,
                           branch=branch,
                           organizers=organizers,
                           co_organizers=co_organizers,
                           track_organizers=track_organizers,
                           attendees=attendees,
                           accepted_sessions=accepted_sessions,
                           rejected_sessions=rejected_sessions,
                           draft_sessions=draft_sessions,
                           email_times=email_times,
                           navigation_bar=list_navbar())
