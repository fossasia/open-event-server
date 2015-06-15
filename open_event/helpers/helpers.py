"""Written by - Rafal Kowalski"""
from flask import request
import re


def get_event_id():
    url = request.url
    m = re.search('event\/[0-9]*', url)
    return m.group(0).split('/')[1]