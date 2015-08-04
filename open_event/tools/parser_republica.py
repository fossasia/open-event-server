import requests
import json
from datetime import datetime
from open_event.models.event import Event
from open_event.models.user import User
from open_event.helpers.data import get_or_create
from open_event import current_app

class RepublicaParser(object):

    def __init__(self, url, owner_login):
        self.url = url
        self.owner_login = owner_login

    def parse(self):
        self._parse_event()

    def _parse_event(self):
        events_response = self._get_response(self.url)
        for data in events_response['data']:
            EventSaver(data, self.owner_login).save()

    def _get_response(self, url):
        data_response = requests.get(url).text
        return json.loads(data_response)


class ObjectSaver(object):
    def __init__(self, data, owner_login):
        self.data = data
        self.owner_login = owner_login


class EventSaver(ObjectSaver):
    def save(self):
        title = self.data['title']
        url = self.data['url']
        date = self.data['date']
        locations = self.data['locations'][0]

        with current_app.app_context():
            owner = User.query.filter_by(login=self.owner_login).first()
            get_or_create(Event,
                          name=title,
                          url=url,
                          start_time=datetime.strptime(date[0], '%Y-%m-%d'),
                          end_time=datetime.strptime(date[1], '%Y-%m-%d'),
                          latitude=locations['coords'][0],
                          longitude=locations['coords'][1],
                          location_name=locations["label"],
                          owner=owner.id)


RepublicaParser("http://data.re-publica.de/api/events/test-rp14", "rafal").parse()