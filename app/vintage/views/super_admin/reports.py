from flask import Blueprint
from flask import render_template

from app.helpers.data_getter import DataGetter
from app.views.super_admin import REPORTS, check_accessible, list_navbar
from app.helpers.deployment.heroku import HerokuApi
from app.helpers.deployment.kubernetes import KubernetesApi

sadmin_reports = Blueprint('sadmin_reports', __name__, url_prefix='/admin/reports')


@sadmin_reports.before_request
def verify_accessible():
    return check_accessible(REPORTS)


@sadmin_reports.route('/')
def index_view():
    mails = DataGetter.get_all_mails(count=300)
    notifications = DataGetter.get_all_notifications(count=300)
    activities = DataGetter.get_all_activities(count=600)

    on_heroku = HerokuApi.is_on_heroku()
    on_kubernetes = KubernetesApi.is_on_kubernetes()
    pods_info = None
    logplex_url = None

    if on_kubernetes:
        kubernetes_api = KubernetesApi()
        pods_info = kubernetes_api.get_pods()['items']
    elif on_heroku:
        heroku_api = HerokuApi()
        logplex_url = heroku_api.get_logplex_url()

    return render_template(
        'gentelella/super_admin/reports/reports.html',
        mails=mails,
        notifications=notifications,
        on_heroku=on_heroku,
        logplex_url=logplex_url,
        on_kubernetes=on_kubernetes,
        pods_info=pods_info,
        activities=activities,
        navigation_bar=list_navbar()
    )


@sadmin_reports.route('/kubernetes/logs/<string:pod_name>/')
def kubernetes_log_view(pod_name):
    kubernetes_api = KubernetesApi()
    return kubernetes_api.get_logs(pod=pod_name), 200
