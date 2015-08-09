"""Copyright 2015 Rafal Kowalski"""
import re
import requests
from flask import request
from flask.ext import login
from ..models.event import Event
from ..models.track import Track


def get_event_id():
    url = request.url
    result = re.search('event\/[0-9]*', url)
    return result.group(0).split('/')[1]

def is_event_owner(event_id):
    return Event.query.get(event_id).owner == login.current_user.id

def is_track_name_unique_in_event(form, event_id, *args):
    track_name = form.name.data
    track_id = args[0] if len(args) else None
    tracks = Track.query.filter_by(event_id=event_id, name=track_name)
    if not track_id:
        return tracks.count() == 0
    else:
        for track in tracks.all():
            if str(track.id) == track_id:
                return True
            else:
                return False
        else:
            return True


def send_email_after_account_create(form):
    payload = {'to': form.email.data, 'from': 'open-event@googlegroups.com', 'subject':"Account Created on Open Event", "html":"Your Account Has Been Created! Congratulations!<br /> Your login: " + form.login.data}
    requests.post("https://api.sendgrid.com/api/mail.send.json", data=payload, headers={"Authorization": "Bearer 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"})
