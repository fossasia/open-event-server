import unittest
import json

from tests.unittests.setup_database import Setup
from tests.unittests.utils import OpenEventTestCase
from tests.unittests.api.utils import create_event, get_path, create_services
from tests.unittests.api.utils_post_data import *
from tests.unittests.auth_helper import register, login, logout
from app import current_app as app


class TestPutApiBase(OpenEventTestCase):
    """
    Base class for help testing PUT APIs
    """
    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            register(self.app, u'test@example.com', u'test')
            logout(self.app)
            event_id = create_event(
                name='TestEvent_1', creator_email=u'test@example.com')
            create_services(event_id)

    def _login_user(self):
        """
        Registers an email and logs in.
        """
        with app.test_request_context():
            login(self.app, u'test@example.com', u'test')

    def _put(self, path, data):
        return self.app.put(
            path,
            data=json.dumps(data),
            headers={'content-type': 'application/json'}
        )


class TestPutApi(TestPutApiBase):
    """
    Test PUT APIs against 401 (unauthorized) and
    200 (successful) status codes
    """
    def _test_model(self, name, data, path=None, *args):
        """
        Tests -
        1. Without login, try to do a PUT request and catch 401 error
        2. Login and match 200 response code and make sure that
            data changed
        """
        if not path:
            path = get_path(1) if name == 'event' else get_path(1, name + 's', 1)
        response = self._put(path, data)
        self.assertEqual(401, response.status_code, msg=response.data)
        # login and send the request again
        self._login_user()
        response = self._put(path, data)
        self.assertEqual(200, response.status_code, msg=response.data)
        # surrounded by quotes for strict checking.
        # before PUT, name is TestX_1, after PUT: TestX
        self.assertIn('"Test%s"' % (name[0].upper() + name[1:]), response.data)
        # check more things
        for _ in args:
            self.assertIn(_, response.data, response.data)

    def test_event_api(self):
        self._test_model('event', POST_EVENT_DATA, None, 'Test licence')

    def test_track_api(self):
        self._test_model('track', POST_TRACK_DATA)

    def test_microlocation_api(self):
        self._test_model('microlocation', POST_MICROLOCATION_DATA)

    def test_session_api(self):
        self._test_model('session', POST_SESSION_DATA)

    def test_speaker_api(self):
        self._test_model('speaker', POST_SPEAKER_DATA)

    def test_sponsor_api(self):
        self._test_model('sponsor', POST_SPONSOR_DATA)

    def test_social_link_api(self):
        self._test_model(
            'socialLink', POST_SOCIAL_LINK_DATA, path=get_path(1, 'links', 1)
        )

    def test_session_type_api(self):
        self._test_model(
            'sessionType', POST_SESSION_TYPE_DATA,
            path=get_path(1, 'sessions', 'types', 1)
        )


class TestPutApiMin(TestPutApiBase):
    """
    Test PUT API with payload as just one field.
    """
    def _test_change_json(self, old, new, field):
        old = json.loads(old)
        new = json.loads(new)
        if field.endswith('_id'):
            field = field[:-3]
        for i in old:
            newdata = new[i]
            olddata = old[i]
            if type(newdata) in [dict, list]:
                newdata = ''.join(sorted(json.dumps(newdata)))
            if type(olddata) in [dict, list]:
                olddata = ''.join(sorted(json.dumps(olddata)))
            # compare
            if i != field and newdata != olddata:
                if i != 'version':  # event api version changes always
                    return i
        return False

    def _test_model(self, name, data, path=None, exclude=[]):
        if not path:
            path = get_path(1) if name == 'event' else get_path(1, name + 's', 1)
        self._login_user()
        data_copy = data.copy()
        # loop over keys
        for i in data_copy:
            if i in exclude:
                continue
            # get old
            resp_old = self.app.get(path)
            self.assertEqual(resp_old.status_code, 200)
            # update
            resp = self._put(path, {i: data_copy[i]})
            self.assertEqual(200, resp.status_code,
                             msg='Key: %s\nMsg: %s' % (i, resp.data))
            # check persistence
            status = self._test_change_json(resp_old.data, resp.data, i)
            if status:
                self.assertTrue(0, msg='Key %s changed in %s' % (status, i))

    def test_event_api(self):
        self._test_model('event', POST_EVENT_DATA, exclude=['sub_topic'])

    def test_track_api(self):
        self._test_model('track', POST_TRACK_DATA)

    def test_microlocation_api(self):
        self._test_model('microlocation', POST_MICROLOCATION_DATA)

    def test_session_api(self):
        self._test_model('session', POST_SESSION_DATA)

    def test_speaker_api(self):
        self._test_model('speaker', POST_SPEAKER_DATA)

    def test_sponsor_api(self):
        self._test_model('sponsor', POST_SPONSOR_DATA)

    def test_social_link_api(self):
        self._test_model(
            'socialLink', POST_SOCIAL_LINK_DATA, path=get_path(1, 'links', 1)
        )

    def test_session_type_api(self):
        self._test_model(
            'sessionType', POST_SESSION_TYPE_DATA,
            path=get_path(1, 'sessions', 'types', 1)
        )


if __name__ == '__main__':
    unittest.main()
