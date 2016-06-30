import unittest
import json

from open_event import current_app as app
from open_event.models.user import User

from tests.setup_database import Setup
from tests.utils import OpenEventTestCase
from tests.auth_helper import register, create_user
from utils_post_data import POST_USER_DATA, PUT_USER_DATA


def get_path(*args):
    url = '/api/v2/users'
    if args:
        url += '/' + '/'.join(map(str, args))
    return url


class TestUserApi(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            create_user('em1@gmail.com', 'test')
            create_user('em2@gmail.com', 'test')

    def _login_user(self):
        with app.test_request_context():
            register(self.app, u'em3@gmail.com', u'test')


class TestUserApiGet(TestUserApi):
    def test_get_single(self):
        path = get_path(1)
        resp = self.app.get(get_path(3))
        self.assertEqual(resp.status_code, 404)
        resp = self.app.get(path)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('gmail', resp.data)

    def test_get_list(self):
        path = get_path()
        resp = self.app.get(path)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('gmail', resp.data)

    def test_get_list_paginated(self):
        path = get_path('page')
        resp = self.app.get(path)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('gmail', resp.data)
        resp = self.app.get(path + '?start=3')
        self.assertEqual(resp.status_code, 404)


class TestUserApiWritable(TestUserApi):
    def _post(self, path, data):
        return self.app.post(
            path,
            data=json.dumps(data),
            headers={'content-type': 'application/json'}
        )

    def _put(self, path, data):
        return self.app.put(
            path,
            data=json.dumps(data),
            headers={'content-type': 'application/json'}
        )

    def test_post_api(self):
        path = get_path()
        resp = self._post(path, POST_USER_DATA)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('gmail', resp.data)

    def test_put_api(self):
        path = get_path(1)
        resp = self._put(path, PUT_USER_DATA)
        self.assertEqual(resp.status_code, 401)
        self._login_user()
        resp = self._put(path, PUT_USER_DATA)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('email@domain.com', resp.data)
        self.assertNotIn('gmail', resp.data)
        self.assertIn('TestUser', resp.data)
        # test adding invalid field and resistance
        extraData = PUT_USER_DATA.copy()
        extraData['user_detail']['new_field'] = 'value'
        resp = self._put(path, extraData)
        self.assertEqual(resp.status_code, 200)

    def test_delete_api(self):
        path = get_path(1)
        resp = self.app.delete(path)
        self.assertEqual(resp.status_code, 401)
        self._login_user()
        resp = self.app.delete(path)
        self.assertIn('em1', resp.data)
        resp = self.app.get(path)
        self.assertEqual(resp.status_code, 404)
        # test existance in database (in trash)
        with app.test_request_context():
            user = User.query.get(1)
            self.assertNotEqual(user, None)
            self.assertEqual(user.in_trash, True)


if __name__ == '__main__':
    unittest.main()
