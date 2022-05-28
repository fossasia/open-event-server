import icalendar

from app.api.helpers.calendar.ical import to_ical
from app.api.helpers.ICalExporter import ICalExporter
from tests.factories.event import EventFactoryBasic
from tests.factories.microlocation import MicrolocationSubFactory
from tests.factories.session import SessionFactory
from tests.factories.video_stream import VideoStreamFactoryBase


def test_export_basic(db):
    test_event = EventFactoryBasic(
        identifier='asdfgh',
        name='Hoopa Loopa',
        location_name='Narnia',
        timezone='Asia/Kolkata'
    )
    test_microlocation = MicrolocationSubFactory(
        name='online',
        event=test_event,
    )
    test_session = SessionFactory(
        title='Gooseberry Muffin',
        event=test_event,
        microlocation=test_microlocation,
    )
    db.session.commit()
    test_cal_str = to_ical(test_session.event, include_sessions=True)
    test_cal = icalendar.Calendar.from_ical(test_cal_str)

    event = test_cal.subcomponents[0]
    assert event['summary'] == 'Hoopa Loopa'
    assert event['url'] == 'http://eventyay.com/e/asdfgh'
    assert event['location'] == 'Narnia'

    timezone = test_cal.subcomponents[1]
    assert timezone['TZID'] == 'Asia/Kolkata'

    session = test_cal.subcomponents[2]
    assert session['summary'] == 'Gooseberry Muffin'
    assert session['url'] == f'http://eventyay.com/e/asdfgh/session/{test_session.id}'
    assert (
        session['location']
        == f'online'
    )

    assert ICalExporter.export(test_session.event_id) == test_cal_str
