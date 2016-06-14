"""Copyright 2015 Rafal Kowalski"""
import json
import os
import re
import requests
from flask import request
from itsdangerous import Serializer
from flask.ext import login
from ..models.track import Track


def get_event_id():
    """Get event Id from request url"""
    url = request.url
    result = re.search('event\/[0-9]*', url)
    return result.group(0).split('/')[1]


def is_track_name_unique_in_event(form, event_id, *args):
    """Check unique of track name in event"""
    track_name = form.name.data
    track_id = args[0] if len(args) else None
    tracks = Track.query.filter_by(event_id=event_id, name=track_name)
    if not track_id:
        return tracks.count() == 0
    else:
        for track in tracks.all():
            return str(track.id) == track_id
        return True


HEADERS = {
    "Authorization": ("Bearer SG.55ztiWJxQYuYK7ToThxDPA.rAc929FzcDQsyj" \
                      "VwmIvKlPoc1YVpKCSOwhEFWZvxFT8")
}


def send_email_invitation(email, event_name, link):
    """Send email after account create"""
    payload = {'to': email,
               'from': 'open-event@googlegroups.com',
               'subject': "Invitation to Submit Papers for " + event_name,
               "html": ("Hi %s<br/>" % str(email) + \
                        "You are invited to submit papers for event: %s" % str(event_name) + \
                        "<br/> Visit this link to fill up details: %s" % link)}
    requests.post("https://api.sendgrid.com/api/mail.send.json",
                  data=payload,
                  headers=HEADERS)


def send_email_after_account_create(form):
    """Send email after account create"""
    payload = {'to': form['email'],
               'from': 'open-event@googlegroups.com',
               'subject': "Account Created on Open Event",
               "html": ("Your Account Has Been Created! Congratulations!" \
                        "<br/> Your login: ") + form['email']}
    requests.post("https://api.sendgrid.com/api/mail.send.json",
                  data=payload,
                  headers=HEADERS)


def send_email_confirmation(form, link):
    payload = {'to': form['email'],
               'from': 'open-event@googlegroups.com',
               'subject': "Email Confirmation to Create Account for Open-Event ",
               "html": ("Hi %s<br/>" % str(form['email']) + \
                        "<br/> Please visit this link to confirm your email: %s" % link)}

    requests.post("https://api.sendgrid.com/api/mail.send.json",
                  data=payload,
                  headers=HEADERS)


def send_email_with_reset_password_hash(email, link):
    """Send email with reset password hash"""
    payload = {'to': email,
               'from': 'open-event@googlegroups.com',
               'subject': "Please click to below link",
               "html": "Change password now " + link}
    requests.post("https://api.sendgrid.com/api/mail.send.json",
                  data=payload,
                  headers=HEADERS)


def get_serializer(secret_key=None):
    return Serializer('secret_key')

def get_latest_heroku_release():
    token = os.environ.get('API_TOKEN_HEROKU', None)
    headers = {
        "Accept": "application/vnd.heroku+json; version=3",
        "Authorization": "Bearer " + token,
        "Range": "version ..; max=1, order=desc"
    }
    response = requests.get("https://api.heroku.com/apps/open-event/releases", headers=headers)
    return json.loads(response.text)[0]
