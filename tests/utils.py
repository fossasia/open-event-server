import unittest
from tests.setup_database import Setup

class OpenEventTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def tearDown(self):
        Setup.drop_db()
