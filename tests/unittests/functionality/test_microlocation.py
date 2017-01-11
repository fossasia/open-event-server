import unittest

from app import current_app as app
from app.helpers.data import save_to_db
from app.models.microlocation import Microlocation
from tests.unittests.object_mother import ObjectMother
from tests.unittests.setup_database import Setup
from tests.unittests.utils import OpenEventTestCase


class TestMicrolocationApi(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_add_microlocation_to_db(self):
        with app.test_request_context():
            # create event
            event = ObjectMother.get_event()
            save_to_db(event, 'Event saved')
            # test
            microlocation = ObjectMother.get_microlocation()
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
