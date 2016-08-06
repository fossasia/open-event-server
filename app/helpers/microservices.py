import requests
from app.helpers.data_getter import DataGetter
from flask import request, flash
from flask.ext import login
from app.settings import get_settings


class AppCreator(object):
    def __init__(self, event_id):
        self.event = DataGetter.get_event(event_id)
        self.app_link = ''
        self.app_name = self.event.name
        self.email = self.event.email


class WebAppCreator(AppCreator):
    def __init__(self, event_id):
        super(WebAppCreator, self).__init__(event_id)
        self.app_link = get_settings().get('web_app_url')
    def create(self):
        pass

    def __save(self):
        pass


class AndroidAppCreator(AppCreator):
    def __init__(self, event_id):
        super(AndroidAppCreator, self).__init__(event_id)
        self.app_link = get_settings().get('android_app_url')

    def create(self):
        data = {
            "email": login.current_user.email,
            "app_name": self.app_name,
            "endpoint": request.url_root + "api/v2/events/" + str(self.event.id)
        }
        r = requests.post(self.app_link, json=data)

        if r.status_code == 200:
            flash("Your app is created and sent to your email", "info")
        else:
            flash(r.text, "warning")

    def __save(self):
        pass
