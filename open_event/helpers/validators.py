"""Copyright 2015 Rafal Kowalski"""
from helpers import get_event_id
from data_getter import DataGetter
from wtforms import ValidationError


class CustomDateSessionValidate(object):
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        event = DataGetter.get_event(get_event_id())
        session_start = form['start_time'].data
        session_end = form['end_time'].data
        if session_start != None and session_end != None:
            if not (event.start_time <= session_start and session_end <= event.end_time and session_start < session_end):
                self.message = "Session date should be between Event date"
                raise ValidationError(self.message)