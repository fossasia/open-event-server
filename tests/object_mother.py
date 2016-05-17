"""Copyright 2015 Rafal Kowalski"""
from datetime import datetime
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
                     description="description")

    @staticmethod
    def get_session():
        return Session(title='test',
                       description='dsad',
                       start_time=datetime(2003, 8, 4, 12, 30, 45),
                       end_time=datetime(2003, 8, 4, 12, 30, 45))

    @staticmethod
    def get_microlocation():
        return Microlocation(name="name",
                             latitude=1.0,
                             longitude=1.0)


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
                    nickname="test",
                    email="email@gmail.com")
