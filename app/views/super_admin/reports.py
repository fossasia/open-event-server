import os

import requests
from flask import Blueprint
from flask import render_template

from app.helpers.data_getter import DataGetter
from app.views.super_admin import REPORTS, check_accessible

sadmin_reports = Blueprint('sadmin_reports', __name__, url_prefix='/admin/reports')


@sadmin_reports.before_request
def verify_accessible():
    return check_accessible(REPORTS)


@sadmin_reports.route('/')
def index_view():
    token = os.environ.get('API_TOKEN_HEROKU', None)
    logplex_url = None
    mails = DataGetter.get_all_mails(count=300)
    notifications = DataGetter.get_all_notifications(count=300)
    activities = DataGetter.get_all_activities(count=600)
    if token:
        headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": "Bearer " + token,
        }
        params = {
            "tail": True,
            "dyno": "web.1",
            "lines": 10,
            "source": "app"
        }
        response = requests.post(
            "https://api.heroku.com/apps/open-event/log-sessions",
            headers=headers,
            params=params).json()

        logplex_url = response.get('logplex_url')

    return render_template(
        'gentelella/admin/super_admin/reports/reports.html',
        log_url=logplex_url,
        mails=mails,
        notifications=notifications,
        activities=activities
    )
