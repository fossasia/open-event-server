"""Copyright 2015 Rafal Kowalski"""
from datetime import datetime

from app.models.call_for_papers import CallForPaper
from app.models.custom_forms import CustomForms, session_form_str, speaker_form_str
from app.models.track import Track
from app.models.event import Event
from app.models.session import Session
from app.models.speaker import Speaker
from app.models.microlocation import Microlocation
from app.models.user import User


class ObjectMother(object):
    @staticmethod
    def get_event():
        return Event(name="event1",
                     start_time=datetime(2003, 8, 4, 12, 30, 45),
                     end_time=datetime(2003, 9, 4, 12, 30, 45),
                     location_name='India',
                     topic='Travel & Outdoor',
                     sub_topic='Climbing',
                     type='Camp, Trip, or Retreat')

    @staticmethod
    def get_track(event_id=1):
        return Track(name="name",
                     event_id=event_id,
                     description="description",
                     color="red")

    @staticmethod
    def get_session(event_id=1):
        return Session(title='test',
                       long_abstract='dsad',
                       start_time=datetime(2003, 8, 4, 12, 30, 45),
                       end_time=datetime(2003, 8, 4, 12, 30, 45),
                       event_id=event_id,
                       state='pending')

    @staticmethod
    def get_microlocation(event_id=1):
        return Microlocation(name="name",
                             latitude=1.0,
                             longitude=1.0,
                             event_id=event_id)
    @staticmethod
    def get_custom_form(event_id=1):
        return CustomForms(event_id=event_id,
                           session_form=session_form_str,
                           speaker_form=speaker_form_str)

    @staticmethod
    def get_speaker():
        return Speaker( name="name",
                        email="email@gmail.com",
                        organisation="FOSSASIA",
                        country="India")

    @staticmethod
    def get_user():
        return User(password="test",
                    email="email@gmail.com",
                    is_admin=False)

    @staticmethod
    def get_cfs(event_id=1):
        return CallForPaper(start_date=datetime(2003, 8, 4, 12, 30, 45),
                            end_date=datetime(2003, 9, 4, 12, 30, 45),
                            announcement="Hello there!",
                            event_id=event_id)

