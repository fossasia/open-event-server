"""Copyright 2015 Rafal Kowalski"""
from datetime import datetime

from open_event.models.custom_forms import CustomForms
from open_event.models.track import Track
from open_event.models.event import Event
from open_event.models.session import Session
from open_event.models.speaker import Speaker
from open_event.models.microlocation import Microlocation
from open_event.models.user import User


class ObjectMother(object):
    @staticmethod
    def get_event():
        return Event(name="event1",
                     start_time=datetime(2003, 8, 4, 12, 30, 45),
                     end_time=datetime(2003, 9, 4, 12, 30, 45))

    @staticmethod
    def get_track():
        return Track(name="name",
                     event_id=1,
                     description="description",
                     color="red")

    @staticmethod
    def get_session():
        return Session(title='test',
                       long_abstract='dsad',
                       start_time=datetime(2003, 8, 4, 12, 30, 45),
                       end_time=datetime(2003, 8, 4, 12, 30, 45),
                       event_id=1,
                       state='pending')

    @staticmethod
    def get_microlocation():
        return Microlocation(name="name",
                             latitude=1.0,
                             longitude=1.0,
                             event_id=1)
    @staticmethod
    def get_custom_form():
        return CustomForms(event_id=1,
                           session_form='{"title":{"include":1,"require":1},"subtitle":{"include":0,"require":0},'
                                        '"short_abstract":{"include":1,"require":0},"long_abstract":{"include":0,'
                                        '"require":0},"comments":{"include":1,"require":0},"track":{"include":0,'
                                        '"require":0},"session_type":{"include":0,"require":0},"language":{"include":0,'
                                        '"require":0},"slides":{"include":1,"require":0},"video":{"include":0,'
                                        '"require":0},"audio":{"include":0,"require":0}}',
                           speaker_form='{"name":{"include":1,"require":1},"email":{"include":1,"require":1},'
                                        '"photo":{"include":1,"require":0},"organisation":{"include":1,'
                                        '"require":0},"position":{"include":1,"require":0},"country":{"include":1,'
                                        '"require":0},"short_biography":{"include":1,"require":0},"long_biography"'
                                        ':{"include":0,"require":0},"mobile":{"include":0,"require":0},'
                                        '"website":{"include":1,"require":0},"facebook":{"include":0,"require":0},'
                                        '"twitter":{"include":1,"require":0},"github":{"include":0,"require":0},'
                                        '"linkedin":{"include":0,"require":0}}')
    @staticmethod
    def get_speaker():
        return Speaker( name="name",
                        email="email@gmail.com",
                        organisation="FOSSASIA",
                        country="India")

    @staticmethod
    def get_user():
        return User(login="test",
                    password="test",
                    email="email@gmail.com")
