import json
import unittest

from app import current_app as app
from app.helpers.data import update_role_to_admin
from app.models.user import User
from tests.unittests.auth_helper import register, login, logout
from tests.unittests.setup_database import Setup
from tests.unittests.utils import OpenEventTestCase
from utils_post_data import POST_USER_DATA, PUT_USER_DATA


def get_path(*args):
    url = '/api/v1/users'
    if args:
        url += '/' + '/'.join(map(str, args))
    return url


class TestUserApi(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            register(self.app, 'example@gmail.com', 'test')
            logout(self.app)
            update_role_to_admin({'admin_perm': 'isAdmin'}, user_id=1)

    def _login_user(self):
        with app.test_request_context():
            login(self.app, 'example@gmail.com', 'test')


class TestUserApiGet(TestUserApi):
    def test_get_single(self):
        with app.test_request_context():
            self._login_user()
            path = get_path(1)
            resp = self.app.get(get_path(3))
            self.assertEqual(resp.status_code, 404)
            resp = self.app.get(path)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('gmail', resp.data)

    def test_get_list(self):
        with app.test_request_context():
            self._login_user()
            path = get_path()
            resp = self.app.get(path)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('gmail', resp.data)

    def test_get_list_paginated(self):
        with app.test_request_context():
            self._login_user()
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
        with app.test_request_context():
            path = get_path()
            resp = self._post(path, POST_USER_DATA)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('gmail', resp.data)

    def test_put_api(self):
        with app.test_request_context():
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
            extra_data = PUT_USER_DATA.copy()
            extra_data['user_detail']['new_field'] = 'value'
            resp = self._put(path, extra_data)
            self.assertEqual(resp.status_code, 200)

    def test_delete_api(self):
        with app.test_request_context():
            path = get_path(1)
            resp = self.app.delete(path)
            self.assertEqual(resp.status_code, 401)
            self._login_user()
            resp = self.app.delete(path)
            self.assertIn('example', resp.data)
            resp = self.app.get(path)
            self.assertEqual(resp.status_code, 404)

            # test existence in database (in trash)
            user = User.query.get(1)
            self.assertNotEqual(user, None)
            self.assertEqual(user.in_trash, True)


if __name__ == '__main__':
    unittest.main()
