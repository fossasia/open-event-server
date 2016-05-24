from datetime import datetime
import unittest

from tests.setup_database import Setup
from tests.utils import OpenEventTestCase
from tests.api.utils import create_path

from open_event import current_app as app
from open_event.helpers.data import save_to_db
from open_event.models.event import Event
from open_event.models.session import Session, Level, Format, Language
from open_event.models.speaker import Speaker
from open_event.models.sponsor import Sponsor
from open_event.models.microlocation import Microlocation
from open_event.models.track import Track


class TestGetApiUnrelatedServices(OpenEventTestCase):
    """Test 400 response code for services that don't belong the said event.

    e.g. A Track with id 3 exists and and Event with id 2 exists, but the
    Track doesn't belong to the Event. The following path should give a 400
    response code: '/api/v2/events/2/tracks/3'

    Services include Session, Track, Language, etc. (everything except Event)
    """

    def setUp(self):
        """Create Event (it will have id=1). Create services and associate
        them with event id=2.
        """
        self.app = Setup.create_app()
        with app.test_request_context():
            event = Event(name='TestEvent',
                          start_time=datetime(2013, 8, 4, 12, 30, 45),
                          end_time=datetime(2016, 9, 4, 12, 30, 45))
            event.owner = 1

            microlocation = Microlocation(name='TestMicrolocation',
                                          event_id=2)
            track = Track(name='TestTrack', description='descp', event_id=2)
            level = Level(name='TestLevel', event_id=2)
            format_ = Format(name='TestFormat', label_en='label',
                             event_id=2)
            language = Language(name='TestLanguage', event_id=2)
            session = Session(title='TestSession', description='descp',
                              start_time=datetime(2014, 8, 4, 12, 30, 45),
                              end_time=datetime(2015, 9, 4, 12, 30, 45),
                              event_id=2)
            speaker = Speaker(name='TestSpeaker', email='email@eg.com',
                              organisation='org', country='japan', event_id=2)
            sponsor = Sponsor(name='TestSponsor', event_id=2)

            save_to_db(event, 'Event saved')
            save_to_db(microlocation, 'Microlocation saved')
            save_to_db(track, 'Track saved')
            save_to_db(level, 'Level saved')
            save_to_db(format_, 'Format saved')
            save_to_db(language, 'Language saved')
            save_to_db(session, 'Session saved')
            save_to_db(speaker, 'Speaker saved')
            save_to_db(sponsor, 'Sponsor saved')

            save_to_db(event, 'Event saved')

    def _test_path(self, path):
        """Test response for 400 status code. Also test if response body
        contains 'does not belong to event' string.
        """
        response = self.app.get(path)
        self.assertEqual(response.status_code, 400)
        self.assertIn('does not belong to event', response.data)


    def test_microlocation_api(self):
        with app.test_request_context():
            path = create_path(1, 'microlocations', 1)
            self._test_path(path)

    def test_track_api(self):
        with app.test_request_context():
            path = create_path(1, 'tracks', 1)
            self._test_path(path)

    def test_level_api(self):
        with app.test_request_context():
            path = create_path(1, 'levels', 1)
            self._test_path(path)

    def test_format_api(self):
        with app.test_request_context():
            path = create_path(1, 'formats', 1)
            self._test_path(path)

    def test_language_api(self):
        with app.test_request_context():
            path = create_path(1, 'languages', 1)
            self._test_path(path)

    def test_session_api(self):
        with app.test_request_context():
            path = create_path(1, 'sessions', 1)
            self._test_path(path)

    def test_speaker_api(self):
        with app.test_request_context():
            path = create_path(1, 'speakers', 1)
            self._test_path(path)

    def test_sponsor_api(self):
        with app.test_request_context():
            path = create_path(1, 'sponsors', 1)
            self._test_path(path)


if __name__ == '__main__':
    unittest.main()
