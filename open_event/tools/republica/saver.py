import requests
import json
from datetime import datetime
from open_event.models.event import Event
from open_event.models.speaker import Speaker
from open_event.models.track import Track
from open_event.models.user import User
from open_event.models.session import Session
from open_event.helpers.data import get_or_create
from open_event import current_app

class ObjectSaver(object):

    def __init__(self, url, owner_login, event_id=None):
        self.url = url
        self.owner_login = owner_login
        self.data = self._get_response(self.url)
        self.event_id = event_id

    def _get_response(self, url):
        data_response = requests.get(url).text
        return json.loads(data_response)

class EventSaver(ObjectSaver):

    def parse(self):
        for row in self.data['data']:
            self._save(row)

    def _save(self, row):
        title = row['title']
        url = row['url']
        date = row['date']
        locations = row['locations'][0]

        with current_app.app_context():
            owner = User.query.filter_by(login=self.owner_login).first()
            event = get_or_create(Event,
                          name=title,
                          url=url,
                          start_time=datetime.strptime(date[0], '%Y-%m-%d'),
                          end_time=datetime.strptime(date[1], '%Y-%m-%d'),
                          latitude=locations['coords'][0],
                          longitude=locations['coords'][1],
                          location_name=locations["label"],
                          owner=owner.id)
            self.event_id = event.id

    def get_event_id(self):
        return self.event_id


class SpeakerSaver(ObjectSaver):

    def parse(self):
        for row in self.data['data']:
            self._save(row)

    def _save(self, row):
        name = row['name']
        photo = row['photo']
        biography = row['biography']
        email = ""
        web = row['url']
        twitter = None
        facebook = None
        github = None
        linkedin = None
        organisation = row['organization']
        position = None
        country = ""
        event_id = self.event_id
        sessions = None

        with current_app.app_context():
            new_speaker = get_or_create(Speaker,
                          name=name,
                          photo=photo,
                          biography=biography,
                          email=email,
                          web=web,
                          event_id=event_id,
                          twitter=twitter,
                          facebook=facebook,
                          github=github,
                          linkedin=linkedin,
                          organisation=organisation,
                          position=position,
                          country=country)
        # new_speaker.sessions = todo


class TrackSaver(ObjectSaver):

    def parse(self):
        for row in self.data['data']:
            self._save(row)

    def _save(self, row):
        name = row['label_en']
        description = ""
        track_image_url = None
        event_id = self.event_id

        with current_app.app_context():
            track = get_or_create(Track,
                                  name=name,
                                  description=description,
                                  event_id=event_id,
                                  track_image_url=track_image_url)
        # track.sessions = todo

class SessionSaver(ObjectSaver):

    def parse(self):
        for row in self.data['data']:
            self._save(row)

    def _save(self, row):
        title = row["title"]
        subtitle = None
        description = row["description"]
        try:
            start_time = row["begin"].split('.')[0]
            end_time = row["end"].split('.')[0]
            print start_time, end_time
            event_id = self.event_id
            # abstract = row["abstract"]
            type = None
            level = row["level"]["label_en"]

            with current_app.app_context():
                new_session = get_or_create(Session,
                              title=title,
                              subtitle=subtitle,
                              description=description,
                              start_time=datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S'),
                              end_time=datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S'),
                              event_id=event_id,
                              # abstract=abstract,
                              type=type,
                              level=level)
        except:
            pass
        # new_session.speakers = todo
