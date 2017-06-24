from datetime import datetime
from pytz import timezone

from app.models.speakers_call import SpeakersCall
from app.models.custom_form import CustomForms, session_form_str, speaker_form_str
from app.models.event import Event
from app.models.message_setting import MessageSettings
from app.models.microlocation import Microlocation
from app.models.notification import Notification
from app.models.session import Session
from app.models.speaker import Speaker
from app.models.track import Track
from app.models.user import User


class ObjectMother(object):
    @staticmethod
    def get_event():
        return Event(name="event1",
                     starts_at=(datetime(2003, 8, 4, 12, 30, 45)).replace(tzinfo=timezone('UTC')),
                     ends_at=(datetime(2003, 9, 4, 12, 30, 45)).replace(tzinfo=timezone('UTC')),
                     location_name='India',
                     sub_topic='Climbing',
                     is_sessions_speakers_enabled=True)

    @staticmethod
    def get_track(event_id=1):
        return Track(name="name",
                     event_id=event_id,
                     description="description",
                     color="#caf034")

    @staticmethod
    def get_session(event_id=1):
        return Session(title='test',
                       long_abstract='dsad',
                       starts_at=(datetime(2003, 8, 4, 12, 30, 45)).replace(tzinfo=timezone('UTC')),
                       ends_at=(datetime(2003, 8, 4, 12, 30, 45)).replace(tzinfo=timezone('UTC')),
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
        return Speaker(name="name",
                       email="email@gmail.com",
                       organisation="FOSSASIA",
                       country="India")

    @staticmethod
    def get_user():
        return User(password="test",
                    email="email@gmail.com",
                    is_admin=False)

    @staticmethod
    def get_speakers_call(event_id=1):
        return SpeakersCall(start_date=(datetime(2003, 8, 4, 12, 30, 45)).replace(tzinfo=timezone('UTC')),
                            end_date=(datetime(2003, 9, 4, 12, 30, 45)).replace(tzinfo=timezone('UTC')),
                            announcement="Hello there!",
                            event_id=event_id)

    @staticmethod
    def get_message_settings():
        return MessageSettings(action="Next Event",
                               mail_status=1,
                               notification_status=1,
                               user_control_status=1)

    @staticmethod
    def get_notification():
        user = ObjectMother.get_user()
        return Notification(
            user_id=user.id,
            title="test title",
            message="test msg",
            action="Testing",
            received_at=datetime.now().replace(tzinfo=timezone('UTC')))
