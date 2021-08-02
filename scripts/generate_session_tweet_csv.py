import csv
import readline  # noqa
import sys
from datetime import timedelta

import pytz
import requests
from dateutil import parser

event_identifier = sys.argv[1]
event_url = 'https://api.eventyay.com/v1/events/' + event_identifier

event = requests.get(event_url).json()

event_name = event['data']['attributes']['name']
timezone = pytz.timezone(event['data']['attributes']['timezone'])
print('Event:', event_name)

generate = input('Generate Social Media CSV? (y/N)? ')

if generate.lower() != 'y':
    sys.exit()

default_template = '{speaker_names} will share about "{session_title}" tomorrow at {event_name} #{track_name} {session_link}'

template = input(
    f'Default Template: {default_template}\nPress enter to use default, or type to override: '
)

template = template.strip()

print(f'Using template: { template or default_template }')

duration_string = input(
    'When should the session post on social media be scheduled before the actual session time?\nFor example, 4 hours, 5 minutes, 2 hours 30 minutes, etc.\n'
)
time = parser.parse(duration_string)
delta = timedelta(hours=time.hour, minutes=time.minute, seconds=time.second)

sessions = requests.get(
    event_url
    + '/sessions?page[size]=0&include=track,speakers&filter=[{"or":[{"name":"state","op":"eq","val":"confirmed"},{"name":"state","op":"eq","val":"accepted"}]}]'
).json()


def generate_row(session, track, speakers, template=None):
    if not template:
        template = default_template
    speaker_names = []
    for speaker in speakers:
        speaker_name = speaker['attributes']['name']
        if twitter_link := speaker['attributes']['twitter']:
            speaker_name += ' @' + twitter_link.split('https://twitter.com/')[1]
        speaker_names.append(speaker_name)

    speaker_names = ', '.join(speaker_names)
    session_title = session['attributes']['title']
    track_name = track['attributes']['name']
    session_link = (
        'https://eventyay.com/e/' + event_identifier + '/session/' + session['id']
    )

    text = template.format(
        speaker_names=speaker_names,
        session_title=session_title,
        event_name=event_name,
        track_name=track_name.replace(' ', '_'),
        session_link=session_link,
    )

    photos = list(filter(bool, map(lambda sp: sp['attributes']['photo-url'], speakers)))

    starts_at = session['attributes']['starts-at']
    starts_at_time = parser.parse(starts_at).astimezone(timezone) - delta

    return (
        text,
        photos[0] if photos else None,
        starts_at_time.strftime('%Y-%m-%d %H:%M'),
    )


with open(f'event-{event_identifier}-social-media.csv', mode='w') as csv_file:
    writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    for session in sessions['data']:
        track_link = session['relationships']['track']['data']
        track = list(
            filter(
                lambda data: data['id'] == track_link['id'] and data['type'] == 'track',
                sessions['included'],
            )
        )[0]
        speaker_links = session['relationships']['speakers']['data']
        speakers = []
        for speaker_link in speaker_links:
            speaker = list(
                filter(
                    lambda data: data['id'] == speaker_link['id']
                    and data['type'] == 'speaker',
                    sessions['included'],
                )
            )
            speakers += speaker

        writer.writerow(generate_row(session, track, speakers, template=template))
