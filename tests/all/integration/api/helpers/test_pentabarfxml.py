import unittest
from datetime import datetime
from xml.etree.ElementTree import fromstring

from app.api.helpers.db import save_to_db
from app.api.helpers.pentabarfxml import PentabarfExporter
from app.models import db
from tests.all.integration.utils import OpenEventLegacyTestCase
from tests.factories.event import EventFactoryBasic
from tests.factories.microlocation import MicrolocationFactoryBase
from tests.factories.session import SessionFactory, SessionFactoryBasic
from tests.factories.speaker import SpeakerFactoryBase
from tests.factories.user import UserFactory


class TestPentabarfXML(OpenEventLegacyTestCase):
    def test_export(self):
        """Test to check event contents in pentabarfxml format"""
        with self.app.test_request_context():
            test_event = EventFactoryBasic()
            save_to_db(test_event)
            pentabarf_export = PentabarfExporter()
            pentabarf_string = pentabarf_export.export(test_event.id)
            pentabarf_original = fromstring(pentabarf_string)
            assert pentabarf_original.find('conference/title').text == "example"
            assert pentabarf_original.find('conference/start').text == "2099-12-13"

    def test_export_with_none_ends(self):
        """Test to check event with session with none ends in pentabarfxml format"""
        with self.app.test_request_context():
            session = SessionFactory(title='Cool Session', ends_at=None)
            db.session.commit()
            pentabarf_export = PentabarfExporter()
            pentabarf_string = pentabarf_export.export(session.event.id)
            pentabarf_original = fromstring(pentabarf_string)
            assert pentabarf_original.find('day/room/event/duration').text == None

    def test_export_with_none_starts(self):
        """Test to check event with session with none starts in pentabarfxml format"""
        with self.app.test_request_context():
            session = SessionFactory(title='Cool Session', starts_at=None, ends_at=None)
            db.session.commit()
            pentabarf_export = PentabarfExporter()
            pentabarf_string = pentabarf_export.export(session.event.id)
            pentabarf_original = fromstring(pentabarf_string)
            assert pentabarf_original.find('day/room/event') == None

    def test_export_with_multiple_sessions(self):
        """Test to check event with sessions in pentabarfxml format"""
        with self.app.test_request_context():
            keynote = SessionFactory(
                title='Keynote',
                starts_at=datetime(2019, 10, 15, 10, 25, 46),
                ends_at=datetime(2019, 10, 15, 11, 10, 46),
                track__name='Amazing Track',
                microlocation__name='Great Hall',
                event__name='Awesome Conference',
                event__starts_at=datetime(2019, 10, 15),
                event__ends_at=datetime(2019, 10, 16, 13, 30, 00),
            )

            UserFactory()
            mario = SpeakerFactoryBase.build(name='Mario Behling', user_id=1)
            keynote.speakers = [
                mario,
                SpeakerFactoryBase.build(name='Hong Phuc Dang', user_id=1),
            ]

            SessionFactoryBasic(
                title='Hot Session',
                starts_at=datetime(2019, 10, 15, 11, 30, 00),
                ends_at=datetime(2019, 10, 15, 12, 00, 54),
            )

            future_session = SessionFactoryBasic(
                title='Future Session',
                starts_at=datetime(2019, 10, 16, 9, 15, 30),
                ends_at=datetime(2019, 10, 16, 10, 30, 45),
            )

            future_session.speakers = [
                SpeakerFactoryBase.build(name='Pranav Mistry', user_id=1)
            ]

            MicrolocationFactoryBase(name='Assembly Hall')
            end_session = SessionFactoryBasic(
                title='Bye Bye Session',
                starts_at=datetime(2019, 10, 16, 11, 30, 20),
                ends_at=datetime(2019, 10, 16, 13, 00, 30),
                microlocation_id=2,
            )

            end_session.speakers = [mario]

            db.session.commit()
            pentabarf_export = PentabarfExporter()
            pentabarf_string = pentabarf_export.export(keynote.event.id)
            pentabarf_original = fromstring(pentabarf_string)

            assert pentabarf_original.find('conference/title').text == "Awesome Conference"
            assert pentabarf_original.find('conference/start').text == '2019-10-15'
            assert pentabarf_original.find('conference/end').text == '2019-10-16'
            assert pentabarf_original.find('conference/days').text == '1'

            assert pentabarf_original.find('day/room').attrib['name'] == 'Great Hall'
            assert pentabarf_original.find('day/room/event/title').text == 'Keynote'
            assert pentabarf_original.find('day/room/event/track').text == 'Amazing Track'
            assert pentabarf_original.find('day/room/event/start').text == '10:25'
            assert pentabarf_original.find('day/room/event/duration').text == '00:45'
            assert pentabarf_original.find('day/room/event/persons/person[@id="2"]').text == \
                'Hong Phuc Dang'
            assert len(pentabarf_original.find('day/room/event/persons').getchildren()) == 2

            assert pentabarf_original.find('day/room/event[2]/title').text == 'Hot Session'

            assert pentabarf_original.find('day[2]/room/event/title').text == 'Future Session'
            assert pentabarf_original.find('day[2]/room/event/persons/person').text == \
                'Pranav Mistry'

            assert pentabarf_original.find('day[2]/room[2]').attrib['name'] == 'Assembly Hall'
            assert pentabarf_original.find('day[2]/room[2]/event/title').text == \
                'Bye Bye Session'
            assert pentabarf_original.find('day[2]/room[2]/event/duration').text == '01:30'
            assert pentabarf_original.find('day[2]/room[2]/event/persons/person').text == \
                'Mario Behling'


if __name__ == '__main__':
    unittest.main()
