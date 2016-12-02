import unittest

from app import current_app as app
from app.helpers.data import save_to_db
from tests.unittests.object_mother import ObjectMother
from tests.unittests.setup_database import Setup
from tests.unittests.utils import OpenEventTestCase


class TestEventFunctions(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_add_event_to_db(self):
        with app.test_request_context():
            event = ObjectMother.get_event()
            save_to_db(event, "Event saved")
            self.assertEqual(event.id, event.id)


if __name__ == '__main__':
    unittest.main()
