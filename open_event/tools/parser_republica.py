"""Copyright 2015 Rafal Kowalski"""
import sys
import os

try:
    PWD = os.environ['PWD']
    sys.path.extend([PWD])
except Exception as error:
    print error

from open_event.tools.republica.saver import EventSaver, SpeakerSaver, TrackSaver, SessionSaver


class RepublicaParser(object):
    """Republica Parser main class"""

    def __init__(self, url, event_id, owner_login):
        self.url = url
        self.owner_login = owner_login
        self.event_id = event_id

    def parse(self):
        """Parse data from republica url"""
        self._parse_objects()

    def _parse_objects(self):
        event_saver = EventSaver(self.url + 'events/' + self.event_id, self.owner_login)
        event_saver.parse()
        SpeakerSaver(self.url + self.event_id + '/speakers',
                     self.owner_login,
                     event_id=event_saver.get_event_id()).parse()
        TrackSaver(self.url + self.event_id + '/tracks',
                   self.owner_login,
                   event_id=event_saver.get_event_id()).parse()
        SessionSaver(self.url + self.event_id + '/sessions',
                     self.owner_login,
                     event_id=event_saver.get_event_id()).parse()


RepublicaParser("http://data.re-publica.de/api/", "rp15", "rafal").parse()
