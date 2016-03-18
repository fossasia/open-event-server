"""Copyright 2015 Rafal Kowalski"""
from open_event.helpers.helpers import get_event_id
from open_event.helpers.data_getter import DataGetter
from open_event.models.event import Event
from wtforms import ValidationError


class CustomDateSessionValidate(object):
    """Date session validation class"""

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        event = DataGetter.get_object(Event, get_event_id())
        session_start = form['start_time'].data
        session_end = form['end_time'].data
        if session_start is not None and session_end is not None:
            if not (event.start_time <= session_start < session_end <= event.end_time):
                self.message = "Session date should be between Event date"
                raise ValidationError(self.message)


class CustomDateEventValidate(object):
    """Date Event validation class"""

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        event_start = form['start_time'].data
        event_end = form['end_time'].data
        if event_start is not None and event_end is not None:
            if not event_start < event_end:
                self.message = "Start time has to be less than end time"
                raise ValidationError(self.message)
