from datetime import datetime

from open_event.helpers.data import save_to_db
from open_event.models.user import User
from open_event.models.event import Event
from open_event.models.session import Session
from open_event.models.speaker import Speaker
from open_event.models.sponsor import Sponsor
from open_event.models.microlocation import Microlocation
from open_event.models.session_type import SessionType
from open_event.models.social_link import SocialLink
from open_event.models.track import Track


def create_event(name='TestEvent', creator_email=None):
    """Creates Event and returns its `id`.
    :param name Name of Event
    """
    event = Event(name=name,
                  start_time=datetime(2013, 8, 4, 12, 30, 45),
                  end_time=datetime(2016, 9, 4, 12, 30, 45))
    if creator_email:
        event.creator = User.query.filter_by(email=creator_email).first()
    save_to_db(event, 'Event saved')
    return event.id


def create_session(event_id, serial_no='', **kwargs):
    """Creates Session with track ids and stuff
    """
    kwargs['track'] = Track.query.get(kwargs.get('track', 555))
    kwargs['microlocation'] = Microlocation.query.get(kwargs.get('microlocation', 555))
    kwargs['session_type'] = SessionType.query.get(kwargs.get('session_type', 555))
    kwargs['speakers'] = [
        Speaker.query.get(i) for i in kwargs['speakers']
        if Speaker.query.get(i) is not None
    ]
    session = Session(
        title='TestSession%d_%s' % (event_id, serial_no),
        long_abstract='descp',
        start_time=datetime(2014, 8, 4, 12, 30, 45),
        end_time=datetime(2015, 9, 4, 12, 30, 45),
        event_id=event_id,
        **kwargs
    )
    save_to_db(session, 'Session saved')


def create_services(event_id, serial_no=''):
    """Creates services and associates them with `event_id`. Service names
    have an optional `serial_no` that can be used to make them unique.
    """
    test_micro = 'TestMicrolocation{}_{}'.format(serial_no, event_id)
    test_track = 'TestTrack{}_{}'.format(serial_no, event_id)
    test_session = 'TestSession{}_{}'.format(serial_no, event_id)
    test_speaker = 'TestSpeaker{}_{}'.format(serial_no, event_id)
    test_sponsor = 'TestSponsor{}_{}'.format(serial_no, event_id)
    test_sponsor_type = 'TestSponsorType{}_{}'.format(serial_no, event_id)
    test_session_type = 'TestSessionType{}_{}'.format(serial_no, event_id)
    test_social_link = 'TestSocialLink{}_{}'.format(serial_no, event_id)

    microlocation = Microlocation(name=test_micro, event_id=event_id)
    track = Track(
        name=test_track,
        description='descp',
        event_id=event_id,
        color='red'
    )
    session_type = SessionType(
        name=test_session_type,
        length=30,
        event_id=event_id
    )
    session = Session(title=test_session,
                      long_abstract='descp',
                      start_time=datetime(2014, 8, 4, 12, 30, 45),
                      end_time=datetime(2015, 9, 4, 12, 30, 45),
                      event_id=event_id,
                      session_type=session_type)
    speaker = Speaker(name=test_speaker,
                      email='email@eg.com',
                      organisation='org',
                      country='japan',
                      event_id=event_id)
    sponsor = Sponsor(name=test_sponsor, sponsor_type=test_sponsor_type,
                      event_id=event_id, level='level')
    social_link = SocialLink(
        name=test_social_link,
        link='http://fb.com',
        event_id=event_id
    )

    save_to_db(social_link, 'SocialLink saved')
    save_to_db(session_type, 'SessionType saved')
    save_to_db(microlocation, 'Microlocation saved')
    save_to_db(track, 'Track saved')
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
