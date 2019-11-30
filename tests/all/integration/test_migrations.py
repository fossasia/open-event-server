from app import current_app as app
from tests.all.integration.utils import OpenEventTestCase
from tests.all.integration.setup_database import Setup
from app.views.healthcheck import check_migrations
from populate_db import populate


class TestMigrations(OpenEventTestCase):

    def test_migrations(self):
        """Method to test the database migrations"""

        with app.test_request_context():
            result = check_migrations().split(',')
            self.assertEqual(result[0], 'success')
    
    def test_populate(self):
        """Method to test populate command"""

        with app.test_request_context():
            populate()
