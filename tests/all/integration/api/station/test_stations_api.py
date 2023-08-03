import json

from app.models.station import Station
from tests.factories.event import EventFactoryBasic
from tests.factories.microlocation import MicrolocationFactory, MicrolocationSubFactory
from tests.factories.station import StationFactory


def test_create_station(db, client, jwt, user):
    """Test creating a new station."""
    user.is_super_admin = True
    event = EventFactoryBasic(owner=user)
    microlocation = MicrolocationFactory()
    db.session.commit()

    data = json.dumps(
        {
            "data": {
                "type": "station",
                "attributes": {
                    "station-name": "station name",
                    "station-type": "registration",
                },
                "relationships": {
                    "event": {"data": {"id": str(event.id), "type": "event"}},
                    "microlocation": {
                        "data": {"id": str(microlocation.id), "type": "microlocation"}
                    },
                },
            }
        }
    )

    response = client.post(
        '/v1/station',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 201
    data = json.loads(response.data)['data']
    s_id = data['id']
    station = Station.query.get(s_id)

    assert station.station_name == 'station name'
    assert station.station_type == 'registration'

    attributes = data['attributes']
    assert attributes['station-name'] == station.station_name
    assert attributes['station-type'] == station.station_type
    assert attributes['microlocation-id'] is not None


def test_get_stations(db, client, jwt):
    """Test getting all stations."""
    event = EventFactoryBasic()
    microlocation = MicrolocationSubFactory(
        event=event,
    )
    station = StationFactory(
        event=event,
        microlocation=microlocation,
    )
    db.session.commit()

    response = client.get(
        f'/v1/stations/{station.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 200

    data = json.loads(response.data)['data']
    assert data['id'] == station.id

    attributes = data['attributes']
    assert attributes['station-name'] == station.station_name
    assert attributes['station-type'] == station.station_type


def test_get_stations_by_event(db, client, jwt):
    """Test getting all stations for an event."""
    event = EventFactoryBasic()
    microlocation = MicrolocationSubFactory(
        event=event,
    )
    StationFactory(
        event=event,
        microlocation=microlocation,
    )
    db.session.commit()

    response = client.get(
        f'/v1/events/{event.id}/stations',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 200
    count = Station.query.filter_by(event_id=event.id).count()
    assert json.loads(response.data)['meta']['count'] == count
