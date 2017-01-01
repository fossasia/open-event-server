import json

from app.helpers.data import save_to_db
from app.helpers.data_getter import DataGetter
from app.helpers.helpers import represents_int
from app.helpers.wizard.helpers import get_event_time_field_format
from app.models.microlocation import Microlocation
from app.models.track import Track
from app.models.session_type import SessionType
from app.models.custom_forms import CustomForms
from app.models.call_for_papers import CallForPaper


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


def save_session_speakers(json, event_id=None):
    event_id = event_id if event_id else json['event_id']
    event = DataGetter.get_event(event_id)

    if json['sessions_speakers_enabled']:
        event.has_session_speakers = True
        save_microlocations(json['microlocations'], event_id)
        save_tracks(json['tracks'], event_id)
        save_session_types(json['session_types'], event_id)
        save_call_for_speakers(json['call_for_speakers'], event_id)
        save_custom_forms(json['custom_forms'], event_id)
    else:
        event.has_session_speakers = False
        delete_all_sessions_speakers_data(event_id)

    event.state = json['state'] if event.location_name.strip() != '' else 'Draft'
    save_to_db(event)
    return {
        'event_id': event.id
    }


def save_data(object, data, event_id, attrs):
    ids = []
    for datum in data:
        if datum['id'] and represents_int(datum['id']):
            item = object.query.get(datum['id'])
        else:
            item = object(event_id=event_id)

        for attr in attrs:
            splitted = attr.split('-')
            if len(splitted) > 1:
                setattr(item, splitted[0], datum[splitted[0]] if str(datum[splitted[0]]).strip() != '' else None)
            else:
                setattr(item, attr, datum[attr])

        save_to_db(item)
        ids.append(item.id)

    if len(ids) > 0:
        object.query.filter(~object.id.in_(ids)).filter_by(event_id=event_id).delete(synchronize_session=False)


def save_microlocations(data, event_id):
    save_data(Microlocation, data, event_id, ['floor-number', 'name'])


def save_tracks(data, event_id):
    save_data(Track, data, event_id, ['color', 'name'])


def save_session_types(data, event_id):
    save_data(SessionType, data, event_id, ['length-number', 'name'])


def save_call_for_speakers(data, event_id):
    call_for_papers = DataGetter.get_call_for_papers(event_id).first()
    if not call_for_papers:
        call_for_papers = CallForPaper(event_id=event_id)
    call_for_papers.announcement = data['announcement']
    call_for_papers.timezone = data['timezone']
    call_for_papers.privacy = data['privacy']
    call_for_papers.hash = data['hash']
    call_for_papers.start_date = get_event_time_field_format(data, 'start')
    call_for_papers.end_date = get_event_time_field_format(data, 'end')
    save_to_db(call_for_papers)


def save_custom_forms(data, event_id):
    custom_forms = DataGetter.get_custom_form_elements(event_id)
    if not custom_forms:
        custom_forms = CustomForms(event_id=event_id)
    custom_forms.session_form = json.dumps(data['session'])
    custom_forms.speaker_form = json.dumps(data['speaker'])
    save_to_db(custom_forms)


def delete_all_sessions_speakers_data(event_id):
    Microlocation.query.filter_by(event_id=event_id).delete()
    SessionType.query.filter_by(event_id=event_id).delete()
    Track.query.filter_by(event_id=event_id).delete()
    CallForPaper.query.filter_by(event_id=event_id).delete()
