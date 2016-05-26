from datetime import datetime

from open_event.helpers.data import save_to_db
from open_event.models.event import Event
from open_event.models.session import Session, Level, Format, Language
from open_event.models.speaker import Speaker
from open_event.models.sponsor import Sponsor
from open_event.models.microlocation import Microlocation
from open_event.models.track import Track


def create_event(name='TestEvent'):
    """Creates Event and returns its `id`.
    :param name Name of Event
    """
    event = Event(name=name,
                  start_time=datetime(2013, 8, 4, 12, 30, 45),
                  end_time=datetime(2016, 9, 4, 12, 30, 45))
    event.owner = 1

    save_to_db(event, 'Event saved')
    return event.id


def create_services(event_id):
    """Create services and associates them with `event_id`.
    """
    microlocation = Microlocation(name='TestMicrolocation',
                                  event_id=event_id)
    track = Track(name='TestTrack', description='descp', event_id=event_id)
    level = Level(name='TestLevel', event_id=event_id)
    format_ = Format(name='TestFormat', label_en='label',
                     event_id=event_id)
    language = Language(name='TestLanguage', event_id=event_id)
    session = Session(title='TestSession', description='descp',
                      start_time=datetime(2014, 8, 4, 12, 30, 45),
                      end_time=datetime(2015, 9, 4, 12, 30, 45),
                      event_id=event_id)
    speaker = Speaker(name='TestSpeaker', email='email@eg.com',
                      organisation='org', country='japan', event_id=event_id)
    sponsor = Sponsor(name='TestSponsor', event_id=event_id)

    save_to_db(microlocation, 'Microlocation saved')
    save_to_db(track, 'Track saved')
    save_to_db(level, 'Level saved')
    save_to_db(format_, 'Format saved')
    save_to_db(language, 'Language saved')
    save_to_db(session, 'Session saved')
    save_to_db(speaker, 'Speaker saved')
    save_to_db(sponsor, 'Sponsor saved')


def get_path(*args):
    """Returns API base path with passed arguments appended as path
    parameters.

    '/api/v2/events' + '/arg1/arg2/arg3'

    e.g. create_url(2, 'tracks', 7) -> '/api/v2/events/2/tracks/7'
    """
    url = '/api/v2/events'
    if args:
        url += '/' + '/'.join(map(str, args))
    return url
