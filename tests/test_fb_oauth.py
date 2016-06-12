import unittest

from flask import url_for

from tests.utils import OpenEventTestCase
from tests.setup_database import Setup
from open_event import current_app as app
from open_event.helpers.oauth import FbOAuth
from open_event.helpers.data import get_facebook_auth
from tests.auth_helper import login, logout
from open_event.helpers.data import create_user_oauth
from open_event.helpers.helpers import get_serializer


class TestFacebookOauth(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_redirect(self):
        """Tests whether on redirection the user is being redirected to the proper authentication url of Facebook"""
        with app.test_request_context():
            facebook = get_facebook_auth()
            auth_url = facebook.authorization_url(FbOAuth.get_auth_uri(), access_type='offline')[0]
            self.assertTrue(FbOAuth.get_auth_uri() in auth_url)

    def test_user_already_logged_in(self):
        """If the user is already logged in then on clicking 'Login with Facebook' he should be redirected
            directly to the admin page"""
        with app.test_request_context():
            s = get_serializer()
            data = [u'email@gmail.com', u'test']
            data_hash = s.dumps(data)
            self.app.get(url_for('admin.create_account_after_confirmation_view', hash=data_hash), follow_redirects=True)
            logout(self.app)
            login(self.app, 'email@gmail.com', 'test')
            self.assertTrue('Open Event' in self.app.get('/fCallback/?code=dummy_code&state=dummy_state',
                                                           follow_redirects=True).data)
            self.assertEqual(self.app.get('/fCallback/?code=dummy_code&state=dummy_state').status_code, 302)

    def test_error_return(self):
        """This tests the various errors returned by callback function"""
        with app.test_request_context():
            self.assertTrue("You denied access" in self.app.get(
                "/fCallback/?code=dummy_code&state=dummy_state&error=access denied").data)
            self.assertTrue("Error encountered" in self.app.get(
                "/fCallback/?code=dummy_code&state=dummy_state&error=12234").data)
            self.assertTrue("/login" in self.app.get("/fCallback/?no_code_and_state").data)
            self.assertEqual(self.app.get("/fCallback/1234").status_code, 404)

    def test_if_user_has_user_details(self):
        """Check if user has user_details fields during sign up via facebook"""
        with app.test_request_context():
            user = None
            user_data = {'email': 'test@gmail.com', 'name': 'dsads', 'picture': {'data': {'url': 'aaaa'}}}
            token = 'dsadsads'
            method = 'Facebook'
            user = create_user_oauth(user, user_data, token, method)
            self.assertTrue(user.user_detail)


if __name__ == '__main__':
    unittest.main()
