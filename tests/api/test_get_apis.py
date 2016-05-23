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


class TestGetApi(OpenEventTestCase):
    """Tests for version 2 GET APIs
    """

    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            event = Event(name='TestEvent',
                          start_time=datetime(2013, 8, 4, 12, 30, 45),
                          end_time=datetime(2016, 9, 4, 12, 30, 45))
            event.owner = 1

            microlocation = Microlocation(name='TestMicrolocation',
                                          event_id=1)
            track = Track(name='TestTrack', description='descp', event_id=1)
            level = Level(name='TestLevel', event_id=1)
            format_ = Format(name='TestFormat', label_en='label',
                             event_id=1)
            language = Language(name='TestLanguage', event_id=1)
            session = Session(title='TestSession', description='descp',
                              start_time=datetime(2014, 8, 4, 12, 30, 45),
                              end_time=datetime(2015, 9, 4, 12, 30, 45),
                              event_id=1)
            speaker = Speaker(name='TestSpeaker', email='email@eg.com',
                              organisation='org', country='japan', event_id=1)
            sponsor = Sponsor(name='TestSponsor', event_id=1)

            save_to_db(event, 'Event saved')
            save_to_db(microlocation, 'Microlocation saved')
            save_to_db(track, 'Track saved')
            save_to_db(level, 'Level saved')
            save_to_db(format_, 'Format saved')
            save_to_db(language, 'Language saved')
            save_to_db(session, 'Session saved')
            save_to_db(speaker, 'Speaker saved')
            save_to_db(sponsor, 'Sponsor saved')

    def test_event_api(self):
        with app.test_request_context():
            url = create_path()
            response = self.app.get(url, follow_redirects=True)
            self.assertIn('TestEvent', response.data)
            self.assertEqual(response.status_code, 200)

    def test_track_api(self):
        with app.test_request_context():
            url = create_path(1, 'tracks')
            response = self.app.get(url, follow_redirects=True)
            self.assertIn('TestTrack', response.data)
            self.assertEqual(response.status_code, 200)

    def test_microlocation_api(self):
        with app.test_request_context():
            url = create_path(1, 'microlocations')
            response = self.app.get(url, follow_redirects=True)
            self.assertIn('TestMicrolocation', response.data)
            self.assertEqual(response.status_code, 200)

    def test_level_api(self):
        with app.test_request_context():
            url = create_path(1, 'levels')
            response = self.app.get(url, follow_redirects=True)
            self.assertIn('TestLevel', response.data)
            self.assertEqual(response.status_code, 200)

    def test_format_api(self):
        with app.test_request_context():
            url = create_path(1, 'formats')
            response = self.app.get(url, follow_redirects=True)
            self.assertIn('TestFormat', response.data)
            self.assertEqual(response.status_code, 200)

    def test_language_api(self):
        with app.test_request_context():
            url = create_path(1, 'languages')
            response = self.app.get(url, follow_redirects=True)
            self.assertIn('TestLanguage', response.data)
            self.assertEqual(response.status_code, 200)

    def test_session_api(self):
        with app.test_request_context():
            url = create_path(1, 'sessions')
            response = self.app.get(url, follow_redirects=True)
            self.assertIn('TestSession', response.data)
            self.assertEqual(response.status_code, 200)

    def test_speaker_api(self):
        with app.test_request_context():
            url = create_path(1, 'speakers')
            response = self.app.get(url, follow_redirects=True)
            self.assertIn('TestSpeaker', response.data)
            self.assertEqual(response.status_code, 200)

    def test_sponsor_api(self):
        with app.test_request_context():
            url = create_path(1, 'sponsors')
            response = self.app.get(url, follow_redirects=True)
            self.assertIn('TestSponsor', response.data)
            self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
