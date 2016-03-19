import sys
import os
import json

try:
    PWD = os.environ['PWD']
    sys.path.extend([PWD])
except Exception as error:
    print error

from open_event import current_app
from datetime import datetime
from open_event.helpers.data import get_or_create, save_to_db
from open_event.models.session import Session, Level, Format, Language
from open_event.models.speaker import Speaker
from open_event.models.track import Track
from open_event.models.microlocation import Microlocation
from dateutil.parser import parse
import re


def get_sessions():
    with open('open_event/tools/fossasia/sessions.json', 'r+') as f:
        return json.load(f)['sessions']


def parse_speakers():
    with current_app.app_context():
        with open('open_event/tools/fossasia/speakers.json', 'r+') as f:
            a =  json.load(f)
            for spek in a['speakers']:

                    sp = get_or_create(Speaker,
                                        name=spek['name'],
                                        organisation=spek['organisation'],
                                        email="",
                                        country="",
                                        photo="",
                                        web="",
                                        event_id=event_id,
                                        )
                    # sp.email = spek['email']
                    sp.country = spek['country']
                    sp.photo = spek['photo']
                    sp.web = spek['web']
                    sp.photo = spek['photo']
                    sp.twitter = spek['twitter']
                    sp.linkedin = spek['linkedin']
                    sp.github = spek['github']
                    sp.organisation = spek['organisation']
                    sp.biography = spek['"biography"']
                    save_to_db(sp, "Speaker")


if __name__ == "__main__":
    event_id = sys.argv[1]
    # sessions_json = sys.argv[2]
    sessions = get_sessions()

    try:
        for session_json in sessions:
            with current_app.app_context():
                speakers = []

                for spk in session_json['speakers']:

                    sp = get_or_create(Speaker,
                                        name=spk['name'],
                                        organisation=spk['organisation'],
                                        email="",
                                        country="",
                                        photo="",
                                        web="",
                                        event_id=event_id,
                                        )
                    save_to_db(sp, "Speaker")
                    speakers.append(sp)

                new_session = get_or_create(Session,
                                        title=session_json['title'],
                                        event_id=event_id,
                                        is_accepted=True,
                                        description=session_json['description'],
                                        start_time=parse(session_json['start_time']),
                                        end_time=parse(session_json['end_time']))
                new_session.speakers = speakers
                new_session.track = get_or_create(Track, name=session_json['track']['name'], description="", event_id=event_id, track_image_url="")
                location = session_json["location"]
                pattern_lvl = re.compile(ur'\d')
                level = None
                room = None
                try:
                    room = location.split(',')[1]
                    level = int(re.search(pattern_lvl, location).group(0))
                except Exception as error:
                    print error
                print get_or_create(Microlocation, name=location, floor=level, room=room, event_id=event_id)
                new_session.microlocation = get_or_create(Microlocation,
                                                          latitude=1.333194,
                                                          longitude=103.736132,
                                                          name=location,
                                                          floor=level,
                                                          room=room,
                                                          event_id=event_id)
                save_to_db(new_session, "Session Updated")
    except Exception as e:
        print e
    parse_speakers()