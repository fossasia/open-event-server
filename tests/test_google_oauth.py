import unittest

from flask import url_for

from tests.utils import OpenEventTestCase
from tests.setup_database import Setup
from open_event import current_app as app
from oauthlib.oauth2 import WebApplicationClient
from open_event.helpers.oauth import OAuth
from open_event.helpers.data import get_google_auth
from tests.auth_helper import login, logout
from open_event.helpers.helpers import get_serializer

class TestGoogleOauth(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_user_already_logged_in(self):
        """If the user is already logged in then on clicking 'Login with Google' he should be redirected
            directly to the admin page"""
        with app.test_request_context():
            s = get_serializer()
            data = [u'email@gmail.com', u'test']
            data_hash = s.dumps(data)
            self.app.get(url_for('admin.create_account_after_confirmation_view', hash=data_hash), follow_redirects=True)
            logout(self.app)
            login(self.app, 'email@gmail.com', 'test')
            self.assertTrue('Create event' in self.app.get('/gCallback/?state=dummy_state&code=dummy_code',

                                                               follow_redirects=True).data)
            self.assertEqual(self.app.get('/gCallback/?state=dummy_state&code=dummy_code').status_code, 302)

    def test_redirect(self):
        """Tests whether on redirection the user is being redirected to the proper authentication url of Google"""
        with app.test_request_context():
            google = get_google_auth()
            auth_url = google.authorization_url(OAuth.get_auth_uri(), access_type='offline')[0]
            self.assertTrue(OAuth.get_auth_uri() in auth_url)

    def test_code_in_uri(self):
        """Tests whether the value of code is retained in the uri"""
        client = WebApplicationClient('email@gmail.com')
        uri = "https://gCallback/?state=dummy_state&code=dummy_code"
        self.assertTrue('dummy_code' in client.parse_request_uri_response(uri, state='dummy_state').values())

    def test_error_return(self):
        """This tests the various errors returned by callback function"""
        with app.test_request_context():
            self.assertTrue("You denied access" in self.app.get(
                "/gCallback/?state=dummy_state&code=dummy_code&error=access denied").data)
            self.assertTrue("Error encountered" in self.app.get(
                "/gCallback/?state=dummy_state&code=dummy_code&error=12234").data)
            self.assertTrue("/admin/login" in self.app.get("/gCallback/?no_code_and_state").data)
            self.assertEqual(self.app.get("/gCallback/1234").status_code, 404)


if __name__ == '__main__':
    unittest.main()
