import unittest

from flask_login import login_user

from app.api.helpers.db import save_to_db
from app.api.helpers.export_helpers import create_export_job
from app.models.export_job import ExportJob
from tests.all.integration.auth_helper import create_user
from tests.all.integration.utils import OpenEventTestCase
from tests.factories.event import EventFactoryBasic
from tests.factories.export_job import ExportJobFactory


class TestExportJobHelpers(OpenEventTestCase):
    def test_create_export_job(self):
        """Method to test export job before creation"""

        with self.app.test_request_context():
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
            assert export_job.event.name == 'example'
            assert export_job.user_email == 'user0@example.com'


if __name__ == '__main__':
    unittest.main()
