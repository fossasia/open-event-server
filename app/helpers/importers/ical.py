from __future__ import print_function
import random

from icalendar import Calendar

from app import Session
from app.helpers.data import get_or_create, save_to_db
from app.helpers.importers.helpers import get_valid_event_name, own_event, update_status
from app.models.event import Event
from app.models import db
from app.models.microlocation import Microlocation
from app.models.speaker import Speaker
from app.models.track import Track


class ICalImporter:
    def __init__(self):
        pass

    @staticmethod
    def import_data(file_path, creator_id, task_handle):
        update_status(task_handle, 'Parsing iCal file')
        file = open(file_path, 'rb')
        calendar = Calendar.from_ical(file.read())
        update_status(task_handle, 'Processing event')
        event = Event()

        if 'X-WR-CALNAME' in calendar:
            event.name = get_valid_event_name(calendar.decoded('X-WR-CALNAME'))
        if not event.name and 'X-WR-CALDESC' in calendar:
            event.name = get_valid_event_name(calendar.decoded('X-WR-CALDESC'))
        for session in calendar.walk('vevent'):
            if not event.name:
                event.name = get_valid_event_name(session.decoded('UID'))

            start_time = session.decoded('dtstart')
            end_time = session.decoded('dtend')

            if not event.start_time or start_time < event.start_time:
                event.start_time = start_time
            if not event.end_time or end_time > event.end_time:
                event.end_time = end_time

        if not event.name:
            event.name = 'Un-named Event'
        # Event name set

        if 'X-WR-TIMEZONE' in calendar:
            event.timezone = calendar.decoded('X-WR-TIMEZONE')

        event.has_session_speakers = True
        event.state = 'Published'
        event.privacy = 'public'
        db.session.add(event)

        update_status(task_handle, 'Adding sessions')

        for session_block in calendar.walk('vevent'):
            track_id = None
            if 'CATEGORIES' in session_block:
                categories = session_block['CATEGORIES']
                string_to_hash = categories if not hasattr(categories, '__iter__') else categories[0]
                seed = int('100'.join(list(str(ord(character)) for character in string_to_hash)))
                random.seed(seed)
                color = "#%06x" % random.randint(0, 0xFFFFFF)
                track, _ = get_or_create(Track, event_id=event.id, name=string_to_hash, color=color)
                track_id = track.id

            microlocation, _ = get_or_create(Microlocation, event_id=event.id, name=session_block.decoded('location'))

            session = Session()
            session.track_id = track_id
            session.microlocation_id = microlocation.id
            session.title = session_block.decoded('summary')
            session.short_abstract = session_block.decoded('description')
            session.start_time = session_block.decoded('dtstart')
            session.end_time = session_block.decoded('dtend')
            session.signup_url = session_block.decoded('url')
            session.event_id = event.id
            session.state = 'accepted'
            session.speakers = []
            save_to_db(session, 'Session Updated')

            attendees = []
            if 'attendee' in session_block:
                attendees_dirty = session_block['attendee']
                if hasattr(attendees_dirty, '__iter__'):
                    for attendee in attendees_dirty:
                        attendees.append((attendee.params['CN'], attendee))
                else:
                    attendees.append((attendees_dirty.params['CN'], attendees_dirty))

            for attendee in attendees:
                speaker = Speaker(name=attendee[0], event_id=event.id, email=attendee[1].replace('MAILTO:', ''),
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
