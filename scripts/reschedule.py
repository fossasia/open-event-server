import readline  # noqa
import sys
from getpass import getpass

import pytz
import requests
from dateutil import parser

event_identifier = sys.argv[1]
event_url = 'https://api.eventyay.com/v1/events/' + event_identifier

event = requests.get(event_url).json()

starts_at = event['data']['attributes']['starts-at']
ends_at = event['data']['attributes']['ends-at']
timezone = pytz.timezone(event['data']['attributes']['timezone'])

starts_at = parser.parse(starts_at).astimezone(timezone)
ends_at = parser.parse(ends_at).astimezone(timezone)

print('Event:', event['data']['attributes']['name'])
print('Scheduled Time: ', starts_at, 'to', ends_at)

new_starts_at = parser.parse(input('new starts at: '), fuzzy=True).astimezone(timezone)
new_ends_at = parser.parse(input('new ends at: '), fuzzy=True).astimezone(timezone)

print('New Scheduled Time: ', new_starts_at, 'to', new_ends_at)

reschedule = input('Reschedule? (y/N)? ')

if reschedule.lower() != 'y':
    sys.exit()

username = input('Email: ')
password = getpass()

auth = requests.post(
    'https://api.eventyay.com/auth/session',
    json={'email': username, 'password': password},
)
if auth.status_code != 200:
    print('Auth Error:', auth.json())
    sys.exit(-1)
token = auth.json()['access_token']

data = {
    "data": {
        "attributes": {
            "starts-at": new_starts_at.isoformat(),
            "ends-at": new_ends_at.isoformat(),
        },
        "id": event['data']['id'],
        "type": "event",
    }
}

response = requests.patch(
    event_url,
    json=data,
    headers={'Content-Type': 'application/vnd.api+json', 'Authorization': 'JWT ' + token},
)
if response.status_code != 200:
    print('Error:', response.json())
    sys.exit(-1)

print('Reschedule Successful!')

reschedule_tickets = input('Change ticket sales time? (y/N) ')

if reschedule_tickets.lower() != 'y':
    sys.exit(0)

tickets_url = event_url + '/tickets?fields[ticket]=id&page[size]=0'

tickets = requests.get(tickets_url).json()
ticket_ids = [ticket['id'] for ticket in tickets['data']]

for id in ticket_ids:
    data = {
        "data": {
            "attributes": {"sales-ends-at": new_ends_at.isoformat()},
            "id": id,
            "type": "ticket",
        }
    }

    response = requests.patch(
        'https://api.eventyay.com/v1/tickets/' + id,
        json=data,
        headers={
            'Content-Type': 'application/vnd.api+json',
            'Authorization': 'JWT ' + token,
        },
    )
    if response.status_code != 200:
        print('Error:', response.json())
        sys.exit(-1)

print('Ticket Sales End time rescheduled!')
