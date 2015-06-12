"""Written by - Rafal Kowalski"""
from sqlalchemy.orm.collections import InstrumentedList

from ..models import db
from ..models.track import Track
from ..models.session import Session
from ..models.speaker import Speaker
from flask import flash


class DataManager(object):
    @staticmethod
    def create_track(form, event_id):
        new_track = Track(name=form.name.data,
                              description=form.description.data,
                              event_id=event_id)
        new_track.session = [form.session.data]
        db.session.add(new_track)
        db.session.commit()

    @staticmethod
    def update_track(form, track):
        track.name = form.name.data
        track.description = form.description.data
        track.session = [form.session.data]
        db.session.add(track)
        db.session.commit()

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

    @staticmethod
    def update_session(form, session):
        session.title = form.title.data
        session.description = form.description.data
        session.subtitle = form.subtitle.data
        session.start_time = form.start_time.data
        session.end_time = form.end_time.data
        session.abstract = form.abstract.data
        session.type = form.type.data
        session.level = form.level.data
        session.speakers = InstrumentedList(form.speakers.data if form.speakers.data else [])
        db.session.add(session)
        db.session.commit()

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

    @staticmethod
    def remove_speaker(speaker_id):
        speaker = Speaker.query.get(speaker_id)
        db.session.delete(speaker)
        db.session.commit()
        flash('You successfully delete speaker')

