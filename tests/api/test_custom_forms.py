import unittest
import json

from app.helpers.data import update_or_create
from app.models.custom_forms import CustomForms, SESSION_FORM, \
    SPEAKER_FORM

from tests.auth_helper import register
from tests.setup_database import Setup
from tests.utils import OpenEventTestCase
from tests.api.utils import get_path, create_event
from utils_post_data import *

from app import current_app as app


class TestCustomForms(OpenEventTestCase):
    """
    Test Custom Forms
    """
    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            register(self.app, u'test@example.com', u'test')
            create_event(name='TestEvent0', creator_email='test@example.com')

    def post(self, path, data):
        """
        send a post request to a url
        """
        return self.app.post(
            path,
            data=json.dumps(data),
            headers={'content-type': 'application/json'}
        )

    def test_session(self):
        session = POST_SESSION_DATA.copy()
        SESSION_FORM['comments']['require'] = 1
        session['comments'] = None
        form_str = json.dumps(SESSION_FORM, separators=(',', ':'))
        with app.test_request_context():
            update_or_create(CustomForms, event_id=1, session_form=form_str)
        path = get_path(1, 'sessions')
        resp = self.post(path, session)
        self.assertEqual(resp.status_code, 400)

    def test_speaker(self):
        speaker = POST_SPEAKER_DATA.copy()
        SPEAKER_FORM['github']['require'] = 1
        speaker['github'] = None
        form_str = json.dumps(SPEAKER_FORM, separators=(',', ':'))
        with app.test_request_context():
            update_or_create(CustomForms, event_id=1, speaker_form=form_str)
        path = get_path(1, 'speakers')
        resp = self.post(path, speaker)
        self.assertEqual(resp.status_code, 400)


if __name__ == '__main__':
    unittest.main()
