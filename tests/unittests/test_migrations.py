from app import current_app as app
from tests.unittests.utils import OpenEventTestCase
from tests.unittests.setup_database import Setup
from app.views.healthcheck import check_migrations


class TestMigrations(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_migrations(self):
        """Method to test the database migrations"""

        with app.test_request_context():
            result = check_migrations().split(',')
            self.assertEqual(result[0], 'success')
