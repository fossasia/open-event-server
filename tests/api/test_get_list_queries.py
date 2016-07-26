import unittest
import json

from app.helpers.data import update_role_to_admin
from tests.auth_helper import register, login
from tests.setup_database import Setup
from tests.utils import OpenEventTestCase
from tests.api.utils import get_path, create_event
from utils_post_data import *

from app import current_app as app


class TestGetListQueries(OpenEventTestCase):
    """
    Test Get List Queries
    """
    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            register(self.app, u'test@example.com', u'test')
            update_role_to_admin({'admin_perm': 'isAdmin'}, user_id=1)
            create_event(name='TestEvent0', creator_email='test@example.com')

    def _post(self, path, data):
        """
        send a post request to a url
        """
        resp = self.app.post(
            path,
            data=json.dumps(data),
            headers={'content-type': 'application/json'}
        )
        self.assertEqual(resp.status_code, 201)
        return resp

    def test_event_queries(self):
        with app.test_request_context():
            login(self.app, u'test@example.com', u'test')
            path = get_path()
            resp = self._post(path, POST_EVENT_DATA)
            # check no return
            resp = self.app.get(path + '?state=r@nd0m')
            self.assertEqual(len(resp.data), 3, msg=resp.data)
            # check case-insensitive search
            resp = self.app.get(path + '?contains=test')
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(json.loads(resp.data)), 2)
            # check queryset forwarding
            resp = self.app.get(path + '?contains=test&state=r@nd0m')
            self.assertEqual(len(resp.data), 3)

    def test_event_time_queries(self):
        with app.test_request_context():
            login(self.app, u'test@example.com', u'test')
            path = get_path()
            # Event is of Apr 16
            resp = self.app.get(path + '?end_time_lt=2015-12-31T23:59:59')
            self.assertEqual(len(resp.data), 3, msg=resp.data)
            resp = self.app.get(path + '?start_time_gt=2015-12-31T23:59:59')
            self.assertIn('TestEvent0', resp.data)
            # add one more event of May 16
            resp = self._post(path, POST_EVENT_DATA)
            # test
            resp = self.app.get(path + '?start_time_lt=2016-05-31T23:59:59')
            self.assertEqual(len(json.loads(resp.data)), 2, msg=resp.data)
            resp = self.app.get(path + '?end_time_gt=2016-05-01T00:00:00')
            self.assertIn('"TestEvent"', resp.data)
            self.assertNotIn('TestEvent0', resp.data)

    def test_event_location_queries(self):
        with app.test_request_context():
            login(self.app, u'test@example.com', u'test')
            path = get_path()
            resp = self._post(path, POST_EVENT_DATA)
            # check location smart queries
            resp = self.app.get(path + '?location=SomeBuilding,Berlin')
            self.assertIn('Berlin', resp.data)
            # add another event
            data = POST_EVENT_DATA.copy()
            data['location_name'] = 'SomeBuilding'
            data['searchable_location_name'] = 'SomeBuilding'
            self._post(path, data)
            # get
            resp = self.app.get(path + '?location=SomeBuilding,Berlin')
            self.assertEqual(resp.status_code, 200)
            self.assertIn('SomeBuilding', resp.data)
            self.assertIn('Berlin', resp.data)

    def test_session_time_queries(self):
        with app.test_request_context():
            path = get_path(1, 'sessions')
            resp = self._post(path, POST_SESSION_DATA)
            # 2016-05-30 8:47 to 9:47
            # normal
            resp = self.app.get(path)
            self.assertIn('TestSession', resp.data)
            # check results when query exists
            for _ in ['start_time_lt', 'end_time_lt']:
                resp = self.app.get(path + '?%s=2014-05-12T00:00:00' % _)
                self.assertNotIn('TestSession', resp.data)
                resp = self.app.get(path + '?%s=2017-05-12T00:00:00' % _)
                self.assertIn('TestSession', resp.data)
            for _ in ['start_time_gt', 'end_time_gt']:
                resp = self.app.get(path + '?%s=2018-05-12T00:00:00' % _)
                self.assertNotIn('TestSession', resp.data)
                resp = self.app.get(path + '?%s=2015-05-12T00:00:00' % _)
                self.assertIn('TestSession', resp.data)


if __name__ == '__main__':
    unittest.main()
