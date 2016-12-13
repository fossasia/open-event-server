from app.helpers.data_getter import DataGetter


def get_tracks_json(event_id):
    tracks = DataGetter.get_tracks(event_id)
    data = []
    for track in tracks:
        data.append(track.serialize)
    return data


def get_session_types_json(event_id):
    session_types = DataGetter.get_session_types_by_event_id(event_id)
    data = []
    for session_type in session_types:
        data.append(session_type.serialize)
    return data


def get_microlocations_json(event_id):
    microlocations = DataGetter.get_microlocations(event_id)
    data = []
    for microlocation in microlocations:
        data.append(microlocation.serialize)
    return data

