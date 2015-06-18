"""Copyright 2015 Rafal Kowalski"""
import re
from flask import request



def get_event_id():
    url = request.url
    result = re.search('event\/[0-9]*', url)
    return result.group(0).split('/')[1]
