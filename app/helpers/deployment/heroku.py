import os

import requests


class HerokuApi:
    token = os.environ.get('API_TOKEN_HEROKU', '')
    namespace = 'default'
    headers = {}
    api_url = "https://api.heroku.com/apps/%s/" % os.environ.get('HEROKU_APP_NAME', 'open-event')

    def __init__(self):
        self.headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": "Bearer " + self.token,
        }

    def get(self, endpoint, headers=None, params=None):
        """
        Make a GET request
        :param params:
        :param headers:
        :param endpoint:
        :return:
        """
        if not headers:
            headers = self.headers
        return requests.get(self.api_url + endpoint, headers=headers, verify=False, params=params).json()

    def get_latest_release(self):
        """
        Get the latest heroku release
        :return:
        """
        new_headers = self.headers
        new_headers['Range'] = "version ..; max=1, order=desc"
        return self.get('releases', headers=new_headers)[0]

    def get_logplex_url(self):
        """
        :return:
        """
        params = {
            "tail": True,
            "dyno": "web.1",
            "lines": 100,
            "source": "app"
        }
        return self.get('log-sessions', params=params).get('logplex_url')

    @staticmethod
    def is_on_heroku():
        return 'API_TOKEN_HEROKU' in os.environ
