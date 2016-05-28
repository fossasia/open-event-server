import unittest

from tests.object_mother import ObjectMother
from tests.utils import OpenEventTestCase
from tests.setup_database import Setup
from tests.auth_helper import register, logout
from open_event import current_app as app
from open_event.models import db
from open_event.forms.admin.track_form import TrackForm
from open_event.helpers.data import DataManager


class TestSessionForm(OpenEventTestCase):

    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            db.session.add(ObjectMother.get_event())
            db.session.commit()

    @staticmethod
    def _create_track():
        form = TrackForm()
        form.name.data = 'SomeTrack'
        form.description.data = 'With Description'
        form.track_image_url.data = 'https://example.com/image.gif'
        DataManager().create_track(form, 1)

    @staticmethod
    def _delete_track():
        DataManager().remove_track(1)

    def test_track_at_session_form(self):
        register(self.app, 'test_user', 'email@example.com', 'test_pwd')
        # User is registered and logged in

        with app.test_request_context():
            self._create_track()
            response = self.app.get('/admin/event/1/session/new',
                              follow_redirects=True)
            self.assertIn('SomeTrack', response.data)
            self._delete_track()

        logout(self.app)


if __name__ == '__main__':
    unittest.main()
