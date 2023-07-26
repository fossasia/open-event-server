import json

from tests.factories.speaker import SpeakerFactory


def test_get_registration_stats(db, client, jwt):
    """Test get registration stats endpoint."""
    speaker = SpeakerFactory()
    db.session.add(speaker)
    db.session.commit()

    response = client.get(
        '/v1/user-check-in/stats/event/1?session_ids=1',
        headers=jwt,
    )

    result = {
        "session_stats": [
            {
                "check_in": 0,
                "check_out": 0,
                "manual_count": {},
                "session_id": "1",
                "session_name": "example",
                "speakers": [],
                "track_name": "example",
            }
        ],
        "total_attendee": 0,
        "total_not_checked_in": 0,
        "total_registered": 0,
        "total_session_checked_in": 0,
        "total_session_checked_out": 0,
        "total_track_checked_in": 0,
        "total_track_checked_out": 0,
        "track_stats": [],
    }

    assert response.status_code == 200
    assert json.loads(response.data) == result
