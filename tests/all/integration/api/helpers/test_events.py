import unittest

from app.api.helpers.db import get_count, save_to_db
from app.api.helpers.events import (
    create_custom_forms_for_attendees,
    create_custom_forms_for_sessions,
    create_custom_forms_for_speakers,
)
from app.models.custom_form import CustomForms
from tests.all.integration.utils import OpenEventTestCase
from tests.factories.event import EventFactoryBasic


class TestEventUtilities(OpenEventTestCase):
    def test_should_create_attendee_forms(self):
        """Method to test custom forms for attendees of an event."""
        with self.app.test_request_context():
            event = EventFactoryBasic()
            save_to_db(event)
            create_custom_forms_for_attendees(event)
            self.assertEqual(get_count(CustomForms.query), 28)

    def test_should_create_speaker_forms(self):
        """Method to test custom forms for attendees of an event."""
        with self.app.test_request_context():
            event = EventFactoryBasic()
            save_to_db(event)
            create_custom_forms_for_speakers(event)
            self.assertEqual(get_count(CustomForms.query), 21)

    def test_should_create_session_forms(self):
        """Method to test custom forms for attendees of an event."""
        with self.app.test_request_context():
            event = EventFactoryBasic()
            save_to_db(event)
            create_custom_forms_for_sessions(event)
            self.assertEqual(get_count(CustomForms.query), 12)


if __name__ == '__main__':
    unittest.main()
