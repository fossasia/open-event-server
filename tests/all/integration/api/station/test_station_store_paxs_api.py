import json

from app.models.station_store_pax import StationStorePax
from tests.factories.event import EventFactoryBasic
from tests.factories.microlocation import MicrolocationSubFactory
from tests.factories.session import SessionSubFactory
from tests.factories.station import StationFactory
from tests.factories.station_store_pax import StationStorePaxFactory


def test_create_station_store_pax(db, client, jwt, user):
    """Test that a station store pax can be created."""
    user.is_super_admin = True
    event = EventFactoryBasic()
    microlocation = MicrolocationSubFactory(
        event=event,
    )
    station = StationFactory(
        event=event, microlocation=microlocation, station_type='registration'
    )
    session = SessionSubFactory(
        event=event,
        microlocation=microlocation,
    )
    db.session.commit()

    data = json.dumps(
        {
            "data": {
                "type": "station-store-pax",
                "attributes": {"current_pax": 10},
                "relationships": {
                    "station": {"data": {"id": str(station.id), "type": "station"}},
                    "session": {"data": {"id": str(session.id), "type": "session"}},
                },
            }
        }
    )

    response = client.post(
        '/v1/station-store-paxs',
        data=data,
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 201

    data = response.json["data"]
    assert data["type"] == "station-store-pax"

    attributes = data["attributes"]
    assert attributes["current-pax"] == 10
    assert attributes["created-at"] is not None
    assert attributes["modified-at"] is not None


def test_get_station_store_pax(db, client, jwt):
    """Test that a station store pax can be retrieved."""
    event = EventFactoryBasic()
    microlocation = MicrolocationSubFactory(
        event=event,
    )
    station = StationFactory(
        event=event, microlocation=microlocation, station_type='registration'
    )
    session = SessionSubFactory(
        event=event,
        microlocation=microlocation,
    )
    StationStorePaxFactory(
        station=station,
        session=session,
    )
    db.session.commit()

    response = client.get(
        f"/v1/stations/{station.id}/sessions/{session.id}/station-store-paxs",
        headers=jwt,
    )

    assert response.status_code == 200

    count = StationStorePax.query.filter_by(
        station_id=station.id, session_id=session.id
    ).count()
    assert len(response.json["data"]) == count
