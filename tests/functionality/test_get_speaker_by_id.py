import unittest
from tests.utils import OpenEventTestCase
from tests.setup_database import Setup
from tests.object_mother import ObjectMother
from open_event import current_app as app
from open_event.helpers.data import save_to_db

class TestGetSpeakerById(OpenEventTestCase):

    def test_get_speaker_by_id(self):
        speaker = ObjectMother.get_speaker()
        with app.test_request_context():
            save_to_db(speaker, "Speaker saved")
            response = self.app.get('/api/v1/event/speakers/1')
            self.assertEqual(response.status_code,200)

if __name__ == '__main__':
    unittest.main()
