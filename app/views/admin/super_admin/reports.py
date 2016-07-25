import os
import requests
from flask_admin import expose
from app.views.admin.super_admin.super_admin_base import SuperAdminBaseView


class SuperAdminReportsView(SuperAdminBaseView):
    @expose('/')
    def index_view(self):
        token = os.environ.get('API_TOKEN_HEROKU', None)
        logplex_url = None

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

        return self.render(
            '/gentelella/admin/super_admin/reports/reports.html',
            log_url=logplex_url)
