"""Copyright 2015 Rafal Kowalski"""
import re
from flask import request
from flask.ext import login
from ..models.event import Event

def get_event_id():
    url = request.url
    result = re.search('event\/[0-9]*', url)
    return result.group(0).split('/')[1]

def is_event_owner(event_id):
    return Event.query.get(event_id).owner == login.current_user.id