"""Copyright 2015 Rafal Kowalski"""
from ..models.event import Event
from ..models.session import Session
from ..models.track import Track
from ..models.speaker import Speaker
from ..models.sponsor import Sponsor
from ..models.microlocation import Microlocation
from ..models.user import User
from ..models.file import File
from open_event.helpers.helpers import get_event_id


class DataGetter:
    @staticmethod
    def get_all_events():
        return Event.query.all()

    @staticmethod
    def get_event(event_id):
        return Event.query.get(event_id)

    @staticmethod
    def get_sessions_by_event_id():
        return Session.query.filter_by(event_id=get_event_id())

    @staticmethod
    def get_tracks(event_id):
        return Track.query.filter_by(event_id=event_id)

    @staticmethod
    def get_track(track_id):
        return Track.query.get(track_id)

    @staticmethod
    def get_sessions(event_id):
        return Session.query.filter_by(event_id=event_id)

    @staticmethod
    def get_session(session_id):
        return Session.query.get(session_id)

    @staticmethod
    def get_speakers(event_id):
        return Speaker.query.filter_by(event_id=event_id)

    @staticmethod
    def get_speaker(speaker_id):
        return Speaker.query.get(speaker_id)

    @staticmethod
    def get_sponsors(event_id):
        return Sponsor.query.filter_by(event_id=event_id)

    @staticmethod
    def get_sponsor(sponsor_id):
        return Sponsor.query.get(sponsor_id)

    @staticmethod
    def get_microlocations(event_id):
        return Microlocation.query.filter_by(event_id=event_id)

    @staticmethod
    def get_microlocation(microlocation_id):
        return Microlocation.query.get(microlocation_id)

    @staticmethod
    def get_event_owner(event_id):
        owner_id = Event.query.get(event_id).owner
        return User.query.get(owner_id).login

    @staticmethod
    def get_all_files():
        files = File.query.all()
        return [(file.name, file.name) for file in files]