import unittest
from tests.utils import OpenEventTestCase
from tests.setup_database import Setup
from tests.object_mother import ObjectMother
from app import current_app as app
from app.helpers.data import save_to_db
from app.models.microlocation import Microlocation

class TestMicrolocationApi(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_add_microlocation_to_db(self):
        microlocation = ObjectMother.get_microlocation()
        with app.test_request_context():
            save_to_db(microlocation, "Microlocation saved")
            self.assertEqual(microlocation.id, 1)
            self.assertEqual(microlocation.event_id, 1)

    def test_multiple_microlocation_for_same_event(self):
        microlocation1 = ObjectMother.get_microlocation()
        microlocation2 = Microlocation(name='test2',
                                       latitude=1.0,
                                       longitude=1.0,
                                       event_id=1)
        self.assertEqual(microlocation1.event_id, 1)
        self.assertEqual(microlocation2.event_id, 1)

if __name__ == '__main__':
    unittest.main()
