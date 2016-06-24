import unittest

from flask import url_for

from open_event import current_app as app
from tests.views.view_test_case import OpenEventViewTestCase


class TestProfile(OpenEventViewTestCase):
    def test_profile_view(self):
        with app.test_request_context():
            rv = self.app.get(url_for('profile.index_view'), follow_redirects=True)
            self.assertTrue("test_super_admin@email.com" in rv.data, msg=rv.data)

    def test_profile_edit(self):
        with app.test_request_context():
            data = {
                'email': self.super_admin.email,
                'full_name': 'Super Hero',
                'facebook': 'https://fb.me/super_hero',
                'contact': '+9622100100',
                'twitter': 'https://t.co/super_hero',
                'details': 'I am a super hero'
            }
            rv = self.app.post(url_for('profile.edit_view'), follow_redirects=True, buffered=True,
                               content_type='multipart/form-data', data=data)
            self.assertTrue("Super Hero" in rv.data, msg=rv.data)


if __name__ == '__main__':
    unittest.main()
