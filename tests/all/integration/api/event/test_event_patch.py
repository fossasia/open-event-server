import json

from tests.factories.event import EventFactoryBasic


def get_event(db):
    event = EventFactoryBasic(location_name='Amsterdam')
    db.session.commit()

    return event


def test_edit_event_default_field(db, client, admin_jwt):
    # Should let the previous value remain unchanged if field is not present in data
    event = get_event(db)

    data = json.dumps(
        {
            'data': {
                'type': 'event',
                'id': str(event.id),
                'attributes': {'timezone': 'Europe/Berlin'},
            }
        }
    )

    response = client.patch(
        f'/v1/events/{event.id}',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
        data=data,
    )

    db.session.refresh(event)

    assert response.status_code == 200
    assert event.location_name == 'Amsterdam'
    assert event.timezone == 'Europe/Berlin'


def test_edit_event_null_field(db, client, admin_jwt):
    # Should let the previous value be nulled if field is null in data
    event = get_event(db)

    assert event.location_name == 'Amsterdam'

    data = json.dumps(
        {
            'data': {
                'type': 'event',
                'id': str(event.id),
                'attributes': {'location-name': None},
            }
        }
    )

    response = client.patch(
        f'/v1/events/{event.id}',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
        data=data,
    )

    db.session.refresh(event)

    assert response.status_code == 200
    assert event.location_name is None
