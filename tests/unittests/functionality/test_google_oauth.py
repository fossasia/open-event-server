import unittest

from oauthlib.oauth2 import WebApplicationClient

from app import current_app as app
from app.helpers.data import get_google_auth
from app.helpers.oauth import OAuth
from tests.unittests.auth_helper import login, logout, register
from tests.unittests.setup_database import Setup
from tests.unittests.utils import OpenEventTestCase


class TestGoogleOauth(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_user_already_logged_in(self):
        """If the user is already logged in then on clicking 'Login with Google' he should be redirected
            directly to the admin page"""
        with app.test_request_context():
            register(self.app, 'email@gmail.com', 'test')
            logout(self.app)
            login(self.app, 'email@gmail.com', 'test')
            self.assertTrue('Open Event' in self.app.get('/gCallback/?state=dummy_state&code=dummy_code',
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
            response = self.app.get("/gCallback/?state=dummy_state&code=dummy_code&error=access denied",
                                    follow_redirects=True)
            self.assertTrue("denied" in response.data, msg=response.data)
            response = self.app.get("/gCallback/?state=dummy_state&code=dummy_code&error=12234", follow_redirects=True)
            self.assertTrue("error" in response.data, msg=response.data)
            self.assertTrue("/login" in self.app.get("/gCallback/?no_code_and_state", follow_redirects=True).data)
            self.assertEqual(self.app.get("/gCallback/1234", follow_redirects=True).status_code, 404)


if __name__ == '__main__':
    unittest.main()
