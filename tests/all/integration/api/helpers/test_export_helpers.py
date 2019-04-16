import unittest

from tests.all.integration.utils import OpenEventTestCase
from tests.all.integration.auth_helper import create_user
from tests.all.integration.setup_database import Setup
from app import current_app as app
from app.api.helpers.export_helpers import create_export_job
from app.factories.export_job import ExportJobFactory
from app.factories.event import EventFactoryBasic
from app.models.export_job import ExportJob
from app.api.helpers.db import save_to_db

from flask_login import login_user


class TestExportJobHelpers(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_create_export_job(self):
        """Method to test export job before creation"""

        with app.test_request_context():
            test_related_event = EventFactoryBasic()
            save_to_db(test_related_event)
            test_export_job = ExportJobFactory()
            save_to_db(test_export_job)
            test_export_job.event = test_related_event
            export_event_id = test_export_job.event.id
            test_task_id = test_export_job.task
            user = create_user(email='user0@example.com', password='password')
            login_user(user)
            create_export_job(test_task_id, export_event_id)
            export_job = ExportJob.query.filter_by(event=test_related_event).first()
            self.assertEqual(export_job.event.name, 'example')
            self.assertEqual(export_job.user_email, 'user0@example.com')


if __name__ == '__main__':
    unittest.main()
