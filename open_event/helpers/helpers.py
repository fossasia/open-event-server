"""Copyright 2015 Rafal Kowalski"""
import re
import requests
from flask import request
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

def send_email_invitation(email, username, event_name, link):
    """Send email after account create"""
    payload = {'to': email,
               'from': 'open-event@googlegroups.com',
               'subject': "Invitation to Submit Papers for " + event_name,
               "html": ("Hi %s<br/>" + \
                        "You are invited to submit papers for event: %s" + \
                        "<br/> Visit this link to fill up details: %s" % (username, event_name, link))}
    requests.post("https://api.sendgrid.com/api/mail.send.json",
                  data=payload,
                  headers=HEADERS)

def send_email_after_account_create(form):
    """Send email after account create"""
    payload = {'to': form['email'],
               'from': 'open-event@googlegroups.com',
               'subject': "Account Created on Open Event",
               "html": ("Your Account Has Been Created! Congratulations!" \
                        "<br/> Your login: ") + form['username']}
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


def is_event_admin(event_id, users):
    """
    :param event_id: Event id
    :param users: User id
    :return: is user admin
    """
    is_admin = False
    for user_obj in users:
        if user_obj.user.id == login.current_user.id:
            for ass in login.current_user.events_assocs:
                if ass.event_id == int(event_id):
                    is_admin = ass.admin
                    if is_event_admin:
                        return is_admin
    return is_admin

