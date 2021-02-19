import icalendar

from app.api.helpers.calendar.ical import to_ical
from app.api.helpers.ICalExporter import ICalExporter
from tests.factories.session import SessionSubFactory


def test_export_basic(db):
    test_session = SessionSubFactory(
        title='Gooseberry Muffin',
        event__name='Hoopa Loopa',
        event__identifier='asdfgh',
        event__location_name='Narnia',
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

    assert ICalExporter.export(test_session.event_id) == test_cal_str
