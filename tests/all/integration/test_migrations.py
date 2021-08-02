from app.views.healthcheck import check_migrations
from populate_db import populate
from tests.all.integration.utils import OpenEventTestCase


class TestMigrations(OpenEventTestCase):
    def test_migrations(self):
        """Method to test the database migrations"""

        with self.app.test_request_context():
            result = check_migrations().split(',')
            assert result[0] == 'success'

    def test_populate(self):
        """Method to test populate command"""

        with self.app.test_request_context():
            populate()