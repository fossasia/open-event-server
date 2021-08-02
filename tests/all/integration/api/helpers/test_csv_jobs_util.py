import unittest
from datetime import datetime

from app.api.helpers.csv_jobs_util import *
from app.models import db
from tests.all.integration.auth_helper import create_user
from tests.all.integration.utils import OpenEventTestCase
from tests.factories import common
from tests.factories.attendee import AttendeeFactory
from tests.factories.custom_form import CustomFormFactory
from tests.factories.order import OrderFactory
from tests.factories.session import SessionSubFactory
from tests.factories.speaker import SpeakerFactory


class TestExportCSV(OpenEventTestCase):
    def test_export_orders_csv(self):
        """Method to check the orders data export"""

        with self.app.test_request_context():
            test_order = OrderFactory(created_at=datetime.now())
            test_order.amount = 2
            field_data = export_orders_csv([test_order])
            assert field_data[1][2] == 'initializing'
            assert field_data[1][5] == '2'

    def test_export_attendees_csv(self):
        """Method to check the attendees data export"""

        with self.app.test_request_context():
            test_attendee = AttendeeFactory()
            test_order = OrderFactory(created_at=datetime.now())
            test_attendee.order = test_order
            custom_forms = CustomFormFactory()
            field_data = export_attendees_csv([test_attendee], [custom_forms])
            assert field_data[1][8] == 'tax id'

    def _test_export_session_csv(self, test_session=None):
        with self.app.test_request_context():
            if not test_session:
                test_session = SessionSubFactory()
            field_data = export_sessions_csv([test_session])
            session_row = field_data[1]

            assert session_row[0] == 'example (accepted)'
            assert session_row[12] == 'accepted'

    def test_export_sessions_csv(self):
        """Method to check sessions data export"""

        with self.app.test_request_context():
            self._test_export_session_csv()

    def test_export_sessions_none_csv(self):
        """Method to check sessions data export with no abstract"""

        with self.app.test_request_context():
            test_session = SessionSubFactory()
            test_session.long_abstract = None
            test_session.level = None
            self._test_export_session_csv(test_session)

    def test_export_sessions_with_details_csv(self):
        """Method to check that sessions details are correct"""

        with self.app.test_request_context():
            test_session = SessionSubFactory(
                short_abstract='short_abstract',
                long_abstract='long_abstract',
                comments='comment',
                level='level',
                created_at=common.date_,
                average_rating=common.average_rating_,
                rating_count=common.rating_count_,
            )
            db.session.commit()
            field_data = export_sessions_csv([test_session])
            session_row = field_data[1]

            assert session_row == \
                [
                    'example (accepted)',
                    test_session.starts_at.astimezone(
                        pytz.timezone(test_session.event.timezone)
                    ).strftime('%B %-d, %Y %H:%M %z'),
                    test_session.ends_at.astimezone(
                        pytz.timezone(test_session.event.timezone)
                    ).strftime('%B %-d, %Y %H:%M %z'),
                    '',
                    '',
                    common.string_,
                    'short_abstract',
                    'long_abstract',
                    'comment',
                    session_row[9],
                    'Yes',
                    'level',
                    'accepted',
                    '',
                    '',
                    'English',
                    common.url_,
                    common.url_,
                    common.url_,
                    common.average_rating_,
                    common.rating_count_,
                ]

    def test_export_speakers_csv(self):
        """Method to check speakers data export"""

        with self.app.test_request_context():
            test_speaker = SpeakerFactory(
                name='Mario Behling',
                mobile='9004345009',
                short_biography='Speaker Bio',
                organisation='FOSSASIA',
                position='position',
                speaking_experience='1',
                sponsorship_required='No',
                city='Berlin',
                country='Germany',
            )
            user = create_user(email='export@example.com', password='password')
            user.id = 2
            field_data = export_speakers_csv([test_speaker])
            speaker_row = field_data[1]
            assert speaker_row[0] == 'Mario Behling'
            assert speaker_row[1] == 'user0@example.com'
            assert speaker_row[2] == ''
            assert speaker_row[3] == '9004345009'
            assert speaker_row[4] == 'Speaker Bio'
            assert speaker_row[5] == 'FOSSASIA'
            assert speaker_row[6] == 'position'
            assert speaker_row[7] == '1'
            assert speaker_row[8] == 'No'
            assert speaker_row[9] == 'Berlin'
            assert speaker_row[10] == 'Germany'
            assert speaker_row[11] == common.url_
            assert speaker_row[12] == common.url_
            assert speaker_row[13] == common.url_
            assert speaker_row[14] == common.url_
            assert speaker_row[15] == common.url_


if __name__ == '__main__':
    unittest.main()
