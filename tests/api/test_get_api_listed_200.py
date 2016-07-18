import unittest

from tests.setup_database import Setup
from tests.utils import OpenEventTestCase
from tests.auth_helper import register, login
from tests.api.utils import get_path, create_event, create_services

from open_event import current_app as app
from open_event.helpers.data import update_role_to_admin


class TestGetApiListed(OpenEventTestCase):
    """Tests for version 2 Listed GET API endpoints.
    e.g. '/events', '/events/1/tracks', etc.
    """

    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            register(self.app, u'test@example.com', u'test')
            # User must be part of the staff to access listed events
            update_role_to_admin({'admin_perm': 'isAdmin'}, user_id=1)
            # Create two instances of event/services

            # event_id is going to be 1
            event_id1 = create_event('TestEvent_1', creator_email=u'test@example.com')
            # event_id is going to be 2
            create_event('TestEvent_2', creator_email=u'test@example.com')

            # Associate services to event_id1
            create_services(event_id1, serial_no=1)
            create_services(event_id1, serial_no=2)

    def _test_path(self, path, service1, service2):
        """Helper function.
        Test response for 200 status code. Also test if response body
        contains event/service name.
        """
        with app.test_request_context():
            login(self.app, u'test@example.com', u'test')
            response = self.app.get(path, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(service1, response.data)
            self.assertIn(service2, response.data)

    def test_event_api(self):
        path = get_path()
        self._test_path(path, 'TestEvent_1', 'TestEvent_2')

    def test_track_api(self):
        path = get_path(1, 'tracks')
        self._test_path(path, 'TestTrack1_1', 'TestTrack2_1')

    def test_microlocation_api(self):
        path = get_path(1, 'microlocations')
        self._test_path(path, 'TestMicrolocation1_1', 'TestMicrolocation2_1')

    def test_session_api(self):
        path = get_path(1, 'sessions')
        self._test_path(path, 'TestSession1_1', 'TestSession2_1')

    def test_speaker_api(self):
        path = get_path(1, 'speakers')
        self._test_path(path, 'TestSpeaker1_1', 'TestSpeaker2_1')

    def test_sponsor_api(self):
        path = get_path(1, 'sponsors')
        self._test_path(path, 'TestSponsor1_1', 'TestSponsor2_1')

    def test_social_link_api(self):
        path = get_path(1, 'links')
        self._test_path(path, 'TestSocialLink1_1', 'TestSocialLink2_1')

    def test_sponsor_types_api(self):
        path = get_path(1, 'sponsors', 'types')
        self._test_path(path, 'TestSponsorType1_1', 'TestSponsorType2_1')

    # special tests

    def test_event_api_filters(self):
        path = get_path() + '?location=r@nd0m'
        resp = self.app.get(path)
        self.assertTrue(len(resp.data) < 4, resp.data)
        self.assertNotIn('TestEvent', resp.data)


if __name__ == '__main__':
    unittest.main()
