import icalendar

from app.api.helpers.calendar.ical import to_ical
from app.api.helpers.ICalExporter import ICalExporter
from tests.factories.event import EventFactoryBasic
from tests.factories.microlocation import MicrolocationSubVideoStreamFactory
from tests.factories.session import SessionFactory
from tests.factories.video_stream import VideoStreamFactoryBase


def test_export_basic(db):
    test_event = EventFactoryBasic(
        identifier='asdfgh',
        name='Hoopa Loopa',
        location_name='Narnia',
    )
    test_video_stream = VideoStreamFactoryBase(
        name="stream",
    )
    test_microlocation = MicrolocationSubVideoStreamFactory(
        name='online',
        video_stream=test_video_stream,
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

    session = test_cal.subcomponents[1]
    assert session['summary'] == 'Gooseberry Muffin'
    assert session['url'] == f'http://eventyay.com/e/asdfgh/session/{test_session.id}'
    assert (
        session['location']
        == f'http://eventyay.com/e/asdfgh/video/stream/{test_video_stream.id}'
    )

    assert ICalExporter.export(test_session.event_id) == test_cal_str
