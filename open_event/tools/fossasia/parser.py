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
from dateutil.parser import parse
def get_sessions():
    with open('open_event/tools/fossasia/sessions.json', 'r+') as f:
        return json.load(f)['sessions']

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
                save_to_db(new_session, "Session Updated")
    except Exception as e:
        print e