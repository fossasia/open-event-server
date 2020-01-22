from tests.all.integration.utils import OpenEventTestCase
from app.views.healthcheck import check_migrations
from populate_db import populate


class TestMigrations(OpenEventTestCase):
    def test_migrations(self):
        """Method to test the database migrations"""

        with self.app.test_request_context():
            result = check_migrations().split(',')
            self.assertEqual(result[0], 'success')

    def test_populate(self):
        """Method to test populate command"""

        with self.app.test_request_context():
            populate()
