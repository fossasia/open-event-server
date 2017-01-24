import random

from pentabarf.PentabarfParser import PentabarfParser

from app.helpers.data import get_or_create, save_to_db
from app.helpers.importers.helpers import update_status, string_to_timedelta, own_event
from app.models import db
from app.models.event import Event
from app.models.microlocation import Microlocation
from app.models.session import Session
from app.models.session_type import SessionType
from app.models.speaker import Speaker
from app.models.track import Track


class PentabarfImporter:
    def __init__(self):
        pass

    @staticmethod
    def import_data(file_path, creator_id, task_handle):

        with open(file_path, 'r') as xml_file:
            string = xml_file.read().replace('\n', '')

        update_status(task_handle, 'Parsing XML file')
        conference_object = PentabarfParser.parse(string)
        update_status(task_handle, 'Processing event')
        event = Event()
        event.start_time = conference_object.start
        event.end_time = conference_object.end
        event.has_session_speakers = True
        event.name = conference_object.title
        event.location_name = conference_object.venue  # + ', ' + conference_object.city
        event.searchable_location_name = conference_object.city
        event.state = 'Published'
        event.privacy = 'public'
        db.session.add(event)
        event_time_updated = False
        update_status(task_handle, 'Adding sessions')
        for day_object in conference_object.day_objects:
            for room_object in day_object.room_objects:
                microlocation, _ = get_or_create(Microlocation, event_id=event.id, name=room_object.name)
                for event_object in room_object.event_objects:
                    session_type_id = None
                    if event_object.type:
                        session_type, _ = get_or_create(SessionType, event_id=event.id,
                                                        name=event_object.type, length=str(30))  # TODO: hardcoded here
                        session_type_id = session_type.id
                    track_id = None
                    if event_object.track:
                        string_to_hash = event_object.track
                        seed = int('100'.join(list(str(ord(character)) for character in string_to_hash)))
                        random.seed(seed)
                        color = "#%06x" % random.randint(0, 0xFFFFFF)
                        track, _ = get_or_create(Track, event_id=event.id, name=event_object.track, color=color)
                        track_id = track.id

                    session = Session()
                    session.track_id = track_id
                    session.microlocation_id = microlocation.id
                    session.session_type_id = session_type_id
                    session.title = event_object.title
                    session.short_abstract = event_object.abstract
                    session.long_abstract = event_object.description
                    session.level = getattr(event_object, 'level', None)  # https://github.com/niranjan94/python-pentabarf-xml/issues/3
                    session.start_time = event_object.date + string_to_timedelta(event_object.start)
                    session.end_time = session.start_time + string_to_timedelta(event_object.duration)
                    session.slides = event_object.slides_url
                    session.video = event_object.video_url
                    session.audio = event_object.audio_url
                    session.signup_url = event_object.conf_url
                    session.event_id = event.id
                    session.state = 'accepted'
                    session.speakers = []
                    save_to_db(session, 'Session Updated')

                    if not event_time_updated:
                        event.start_time = None
                        event.end_time = None
                        event_time_updated = True

                    if not event.start_time or session.start_time < event.start_time:
                        event.start_time = session.start_time
                    if not event.end_time or session.end_time > event.end_time:
                        event.end_time = session.end_time

                    for person_object in event_object.person_objects:
                        name_mix = person_object.name + ' ' + conference_object.title
                        email = ''.join(x for x in name_mix.title() if not x.isspace()) + '@example.com'
                        speaker = Speaker(name=person_object.name, event_id=event.id, email=email,
                                          country='Earth',
                                          organisation='')
                        db.session.add(speaker)
                        session.speakers.append(speaker)
                        db.session.commit()

                    update_status(task_handle, 'Added session "' + session.title + '"')

        update_status(task_handle, 'Saving data')
        save_to_db(event)
        update_status(task_handle, 'Finalizing')
        own_event(event=event, user_id=creator_id)
        return event
