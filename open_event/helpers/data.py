"""Written by - Rafal Kowalski"""
from sqlalchemy.orm.collections import InstrumentedList

from ..models import db
from ..models.track import Track
from ..models.session import Session
from ..models.speaker import Speaker
from ..models.sponsor import Sponsor
from ..models.microlocation import Microlocation
from ..helpers.update_version import VersionUpdater
from flask import flash

def update_version(event_id, is_created, column_to_increment):
    VersionUpdater(event_id=event_id, is_created=is_created, column_to_increment=column_to_increment).update()

class DataManager(object):
    @staticmethod
    def create_track(form, event_id):
        new_track = Track(name=form.name.data,
                              description=form.description.data,
                              event_id=event_id)
        new_track.session = form.session.data
        db.session.add(new_track)
        db.session.commit()
        update_version(event_id, True, "tracks_ver")

    @staticmethod
    def update_track(form, track):
        data = form.data
        del data['session']
        db.session.query(Track).filter_by(id=track.id).update(dict(data))
        track.session = form.session.data
        db.session.add(track)
        db.session.commit()
        update_version(track.event_id, False,"tracks_ver")

    @staticmethod
    def remove_track(track_id):
        track = Track.query.get(track_id)
        db.session.delete(track)
        db.session.commit()
        flash('You successfully delete track')

    @staticmethod
    def create_session(form, event_id):
        new_session = Session(title=form.title.data,
                                  subtitle=form.subtitle.data,
                                  description=form.description.data,
                                  start_time=form.start_time.data,
                                  end_time=form.end_time.data,
                                  event_id=event_id,
                                  abstract=form.abstract.data,
                                  type=form.type.data,
                                  level=form.level.data)
        new_session.speakers = InstrumentedList(form.speakers.data if form.speakers.data else [])
        db.session.add(new_session)
        db.session.commit()
        update_version(event_id, True, "session_ver")

    @staticmethod
    def update_session(form, session):
        data = form.data
        speakers = data["speakers"]
        del data["speakers"]
        db.session.query(Session).filter_by(id=session.id).update(dict(data))
        session.speakers = InstrumentedList(speakers if speakers else [])
        db.session.add(session)
        db.session.commit()
        update_version(session.event_id, False, "session_ver")

    @staticmethod
    def remove_session(session_id):
        session = Session.query.get(session_id)
        db.session.delete(session)
        db.session.commit()
        flash('You successfully delete session')

    @staticmethod
    def create_speaker(form, event_id):
        new_speaker = Speaker(name=form.name.data,
                              photo=form.photo.data,
                              biography=form.biography.data,
                              email=form.email.data,
                              web=form.web.data,
                              event_id=event_id,
                              twitter=form.twitter.data,
                              facebook=form.facebook.data,
                              github=form.github.data,
                              linkedin=form.linkedin.data,
                              organisation=form.organisation.data,
                              position=form.position.data,
                              country=form.country.data)
        new_speaker.sessions = InstrumentedList(form.sessions.data if form.sessions.data else [])
        db.session.add(new_speaker)
        db.session.commit()
        update_version(event_id, True, "speakers_ver")

    @staticmethod
    def update_speaker(form, speaker):
        speaker.name=form.name.data
        speaker.photo=form.photo.data
        speaker.biography=form.biography.data
        speaker.email=form.email.data
        speaker.web=form.web.data
        speaker.twitter=form.twitter.data
        speaker.facebook=form.facebook.data
        speaker.github=form.github.data
        speaker.linkedin=form.linkedin.data
        speaker.organisation=form.organisation.data
        speaker.position=form.position.data
        speaker.country=form.country.data
        speaker.sessions = InstrumentedList(form.sessions.data if form.sessions.data else [])
        db.session.add(speaker)
        db.session.commit()
        update_version(speaker.event_id, False, "speakers_ver")

    @staticmethod
    def remove_speaker(speaker_id):
        speaker = Speaker.query.get(speaker_id)
        db.session.delete(speaker)
        db.session.commit()
        flash('You successfully delete speaker')

    @staticmethod
    def create_sponsor(form, event_id):
        new_sponsor = Sponsor(name=form.name.data,
                              url=form.url.data,
                              event_id=event_id,
                              logo=form.logo.data)
        db.session.add(new_sponsor)
        db.session.commit()
        update_version(event_id, True, "sponsors_ver")

    @staticmethod
    def update_sponsor(form, sponsor):
        data = form.data
        db.session.query(Sponsor).filter_by(id=sponsor.id).update(dict(data))
        db.session.add(sponsor)
        db.session.commit()
        update_version(sponsor.event_id, False, "sponsors_ver")

    @staticmethod
    def remove_sponsor(sponsor_id):
        sponsor = Sponsor.query.get(sponsor_id)
        db.session.delete(sponsor)
        db.session.commit()
        flash('You successfully delete sponsor')

    @staticmethod
    def create_microlocation(form, event_id):
        new_microlocation = Microlocation(name=form.name.data,
                                          latitude=form.latitude.data,
                                          longitude=form.longitude.data,
                                          floor=form.floor.data,
                                          event_id=event_id)
        new_microlocation.session = form.session.data
        db.session.add(new_microlocation)
        db.session.commit()
        update_version(event_id, True, "microlocations_ver")

    @staticmethod
    def update_microlocation(form, microlocation):
        data = form.data
        session = data["session"]
        del data["session"]
        db.session.query(Microlocation).filter_by(id=microlocation.id).update(dict(data))
        microlocation.session = session
        db.session.add(microlocation)
        db.session.commit()
        update_version(microlocation.event_id, False, "microlocations_ver")

    @staticmethod
    def remove_microlocation(microlocation_id):
        microlocation = Microlocation.query.get(microlocation_id)
        db.session.delete(microlocation)
        db.session.commit()
        flash('You successfully delete microlocation')

