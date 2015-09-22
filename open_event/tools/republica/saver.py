"""Copyright 2015 Rafal Kowalski"""
import requests
import json
from datetime import datetime
from open_event.models.event import Event
from open_event.models.speaker import Speaker
from open_event.models.track import Track
from open_event.models.user import User
from open_event.models.session import Session, Level, Format, Language
from open_event.helpers.data import get_or_create, save_to_db
from open_event import current_app

class ObjectSaver(object):
    """Object Saver Main class"""
    def __init__(self, url, owner_login, event_id=None):
        self.url = url
        self.owner_login = owner_login
        self.data = self._get_response(self.url)
        self.event_id = event_id

    def _get_response(self, url):
        """
        :param url: from republica
        :return: json
        """
        data_response = requests.get(url).text
        return json.loads(data_response)

class EventSaver(ObjectSaver):
    """Event saver main class"""
    def parse(self):
        """
        Parse data from response
        """
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
                          )
            self.event_id = event.id

    def get_event_id(self):
        return self.event_id


class SpeakerSaver(ObjectSaver):
    """Speaker saver class"""
    def parse(self):
        """Parse data"""
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
    """Track Saver class"""
    def parse(self):
        """Parse data"""
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
    """Session Saver class"""

    def parse(self):
        """Parse data"""
        for row in self.data['data']:
            self._save(row)

    def _save(self, row):
        title = row["title"]
        subtitle = None
        description = row["description"]
        try:

            start_time = row["begin"].split('.')[0]
            end_time = row["end"].split('.')[0]
            event_id = self.event_id
            abstract = row["abstract"]
            format = None
            level = None
            speakers = []
            track = None

            with current_app.app_context():
                level = get_or_create(Level, name=row["level"]["id"], label_en=row["level"]["label_en"], event_id=event_id )
                format = get_or_create(Format, name=row["format"]["id"], label_en=row["format"]["label_en"], event_id=event_id )
                lang = get_or_create(Language, name=row["lang"]["id"], label_en=row["lang"]["label_en"], label_de=row["lang"]["label_en"], event_id=event_id )
                for speaker in row['speakers']:
                    speakers.append(Speaker.query.filter_by(name=speaker['name']).first())

                new_session = get_or_create(Session,
                              title=title,
                              subtitle=subtitle,
                              description=description,
                              start_time=datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S'),
                              end_time=datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S'),
                              event_id=event_id,
                              abstract=abstract,
                              level=level,
                              format=format,
                              language=lang)
                new_session.speakers = speakers
                new_session.track = Track.query.filter_by(name=row['track']['label_en']).first()
                save_to_db(new_session, "Session Updated")
        except Exception as e:
            print e

