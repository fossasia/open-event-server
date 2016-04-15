"""Copyright 2015 Rafal Kowalski"""
import logging
import os.path
import random
import traceback

from flask import flash, request
from flask.ext import login
from flask.ext.scrypt import generate_password_hash, generate_random_salt
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.sql.expression import exists
from werkzeug import secure_filename

from ..helpers.update_version import VersionUpdater
from ..models import db
from ..models.event import Event, EventsUsers
from ..models.file import File
from ..models.microlocation import Microlocation
from ..models.session import Session, Level, Format, Language
from ..models.speaker import Speaker
from ..models.sponsor import Sponsor
from ..models.track import Track
from ..models.user import User


class DataManager(object):
    """Main class responsible for DataBase managing"""

    @staticmethod
    def create_track(form, event_id):
        """
        Track will be saved to database with proper Event id
        :param form: view data form
        :param event_id: Track belongs to Event by event id
        """
        new_track = Track(name=form.name.data,
                          description=form.description.data,
                          event_id=event_id,
                          track_image_url=form.track_image_url.data)
        new_track.sessions = form.sessions.data
        db.session.query(Session).filter_by(id=form.sessions.data).track = new_track.id
        save_to_db(new_track, "Track saved")
        update_version(event_id, False, "tracks_ver")
        sessions = form.sessions.data
        if sessions:
            update_version(event_id, False, "session_ver")

    @staticmethod
    def update_track(form, track):
        """
        Track will be updated in database
        :param form: view data form
        :param track: object contains all earlier data
        """
        data = form.data
        del data['sessions']
        db.session.query(Track) \
            .filter_by(id=track.id) \
            .update(dict(data))
        track.sessions = form.sessions.data
        db.session.query(Session).filter_by(id=form.sessions.data).track = track.id
        save_to_db(track, "Track updated")
        update_version(track.event_id, False, "tracks_ver")
        sessions = form.sessions.data
        if sessions:
            update_version(track.event_id, False, "session_ver")

    @staticmethod
    def remove_track(track_id):
        """
        Track will be removed from database
        :param track_id: Track id to remove object
        """
        track = Track.query.get(track_id)
        delete_from_db(track, "Track deleted")
        flash('You successfully deleted track')

    @staticmethod
    def create_session(form, event_id, is_accepted=True):
        """
        Session will be saved to database with proper Event id
        :param form: view data form
        :param event_id: Session belongs to Event by event id
        """
        new_session = Session(title=form.title.data,
                              subtitle=form.subtitle.data,
                              description=form.description.data,
                              start_time=form.start_time.data,
                              end_time=form.end_time.data,
                              event_id=event_id,
                              abstract=form.abstract.data)

        new_session.speakers = InstrumentedList(form.speakers.data if form.speakers.data else [])
        new_session.microlocation = form.microlocation.data
        new_session.format = form.format.data
        new_session.level = form.level.data
        new_session.is_accepted = is_accepted
        save_to_db(new_session, "Session saved")
        update_version(event_id, False, "session_ver")

    @staticmethod
    def update_session(form, session):
        """
        Session will be updated in database
        :param form: view data form
        :param session: object contains all earlier data
        """
        data = form.data
        speakers = data["speakers"]
        microlocation = data["microlocation"]
        level = data["level"]
        format = data["format"]
        language = data["language"]
        del data["speakers"]
        del data["microlocation"]
        del data["level"]
        del data["format"]
        del data["language"]
        db.session.query(Session) \
            .filter_by(id=session.id) \
            .update(dict(data))
        session.speakers = InstrumentedList(speakers if speakers else [])
        session.microlocation = microlocation
        session.format = format
        session.level = level
        session.language = language
        save_to_db(session, "Session updated")
        update_version(session.event_id, False, "session_ver")

    @staticmethod
    def remove_session(session_id):
        """
        Session will be removed from database
        :param session_id: Session id to remove object
        """
        session = Session.query.get(session_id)
        delete_from_db(session, "Session deleted")
        flash('You successfully delete session')

    @staticmethod
    def create_speaker(form, event_id):
        """
        Speaker will be saved to database with proper Event id
        :param form: view data form
        :param event_id: Speaker belongs to Event by event id
        """
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
        save_to_db(new_speaker, "Speaker saved")
        update_version(event_id, False, "speakers_ver")

    @staticmethod
    def update_speaker(form, speaker):
        """
        Speaker will be updated in database
        :param form: view data form
        :param speaker: object contains all earlier data
        """
        data = form.data
        del data['sessions']
        db.session.query(Speaker) \
            .filter_by(id=speaker.id) \
            .update(dict(data))
        speaker.sessions = InstrumentedList(form.sessions.data if form.sessions.data else [])
        save_to_db(speaker, "Speaker updated")
        update_version(speaker.event_id, False, "speakers_ver")

    @staticmethod
    def remove_speaker(speaker_id):
        """
        Speaker will be removed from database
        :param speaker_id: Speaker id to remove object
        """
        speaker = Speaker.query.get(speaker_id)
        delete_from_db(speaker, "Speaker deleted")
        flash('You successfully delete speaker')

    @staticmethod
    def create_sponsor(form, event_id):
        """
        Sponsor will be saved to database with proper Event id
        :param form: view data form
        :param event_id: Sponsor belongs to Event by event id
        """
        new_sponsor = Sponsor(name=form.name.data,
                              url=form.url.data,
                              event_id=event_id,
                              logo=form.logo.data)
        save_to_db(new_sponsor, "Sponsor saved")
        update_version(event_id, False, "sponsors_ver")

    @staticmethod
    def update_sponsor(form, sponsor):
        """
        Sponsor will be updated in database
        :param form: view data form
        :param sponsor: object contains all earlier data
        """
        data = form.data
        db.session.query(Sponsor).filter_by(id=sponsor.id).update(dict(data))
        save_to_db(sponsor, "Sponsor updated")
        update_version(sponsor.event_id, False, "sponsors_ver")

    @staticmethod
    def remove_sponsor(sponsor_id):
        """
        Sponsor will be removed from database
        :param sponsor_id: Sponsor id to remove object
        """
        sponsor = Sponsor.query.get(sponsor_id)
        delete_from_db(sponsor, "Sponsor deleted")
        flash('You successfully delete sponsor')

    @staticmethod
    def create_level(form, event_id):
        """
        Level will be saved to database with proper Event id
        :param form: view data form
        :param event_id: Level belongs to Event by event id
        """
        new_level = Level(name=form.name.data,
                          label_en=form.label_en.data,
                          event_id=event_id)
        save_to_db(new_level, "Level saved")
        update_version(event_id, False, "session_ver")

    @staticmethod
    def update_level(form, level, event_id):
        """
        Level will be updated in database
        :param form: view data form
        :param level: object contains all earlier data
        """
        data = form.data
        db.session.query(Level).filter_by(id=level.id).update(dict(data))
        save_to_db(level, "Level updated")
        update_version(event_id, False, "session_ver")

    @staticmethod
    def remove_level(level_id):
        """
        Level will be removed from database
        :param level_id: Level id to remove object
        """
        level = Level.query.get(level_id)
        delete_from_db(level, "Level deleted")
        flash('You successfully delete level')

    @staticmethod
    def create_format(form, event_id):
        """
        Format will be saved to database with proper Event id
        :param form: view data form
        :param event_id: Format belongs to Event by event id
        """
        new_format = Format(name=form.name.data,
                            label_en=form.label_en.data,
                            event_id=event_id)
        save_to_db(new_format, "Format saved")
        update_version(event_id, False, "session_ver")

    @staticmethod
    def update_format(form, format, event_id):
        """
        Format will be updated in database
        :param form: view data form
        :param format: object contains all earlier data
        """
        data = form.data
        db.session.query(Format).filter_by(id=format.id).update(dict(data))
        save_to_db(format, "Format updated")
        update_version(event_id, False, "session_ver")

    @staticmethod
    def remove_format(format_id):
        """
        Format will be removed from database
        :param format_id: Format id to remove object
        """
        format = Format.query.get(format_id)
        delete_from_db(format, "Format deleted")
        flash('You successfully delete format')

    @staticmethod
    def create_language(form, event_id):
        """
        Language will be saved to database with proper Event id
        :param form: view data form
        :param event_id: language belongs to Event by event id
        """
        new_language = Language(name=form.name.data,
                                label_en=form.label_en.data,
                                label_de=form.label_de.data,
                                event_id=event_id)
        save_to_db(new_language, "Language saved")
        update_version(event_id, False, "session_ver")

    @staticmethod
    def update_language(form, language, event_id):
        """
        Language will be updated in database
        :param form: view data form
        :param language: object contains all earlier data
        """
        data = form.data
        db.session.query(Language).filter_by(id=language.id).update(dict(data))
        save_to_db(language, "Language updated")
        update_version(event_id, False, "session_ver")

    @staticmethod
    def remove_language(language_id):
        """
        Language will be removed from database
        :param language_id: language id to remove object
        """
        language = Language.query.get(language_id)
        delete_from_db(language, "Language deleted")
        flash('You successfully delete language')

    @staticmethod
    def create_microlocation(form, event_id):
        """
        Microlocation will be saved to database with proper Event id
        :param form: view data form
        :param event_id: Microlocation belongs to Event by event id
        """
        new_microlocation = Microlocation(name=form.name.data,
                                          latitude=form.latitude.data,
                                          longitude=form.longitude.data,
                                          floor=form.floor.data,
                                          room=form.room.data,
                                          event_id=event_id)
        save_to_db(new_microlocation, "Microlocation saved")
        update_version(event_id, False, "microlocations_ver")

    @staticmethod
    def update_microlocation(form, microlocation):
        """
        Microlocation will be updated in database
        :param form: view data form
        :param microlocation: object contains all earlier data
        """
        data = form.data
        if "session" in data.keys():
            session = data["session"]
            del data["session"]
        db.session.query(Microlocation) \
            .filter_by(id=microlocation.id) \
            .update(dict(data))
        save_to_db(microlocation, "Microlocation updated")
        update_version(microlocation.event_id, False, "microlocations_ver")

    @staticmethod
    def remove_microlocation(microlocation_id):
        """
        Microlocation will be removed from database
        :param microlocation_id: Sponsor id to remove object
        """
        microlocation = Microlocation.query.get(microlocation_id)
        delete_from_db(microlocation, "Microlocation deleted")
        flash('You successfully delete microlocation')

    @staticmethod
    def create_user(form):
        user = User()
        form.populate_obj(user)
        # we hash the users password to avoid saving it as plaintext in the db,
        # remove to use plain text:
        salt = generate_random_salt()
        password = form.password.data
        user.password = generate_password_hash(password, salt)
        hash = random.getrandbits(128)
        user.reset_password = str(hash)

        user.salt = salt
        user.role = 'speaker'
        save_to_db(user, "User created")
        return user

    @staticmethod
    def update_user(form, reset_hash):
        user = User.query.filter_by(reset_password=reset_hash).first()
        salt = generate_random_salt()
        password = form.password.data
        user.password = generate_password_hash(password, salt)
        new_hash = random.getrandbits(128)
        user.reset_password = new_hash
        user.salt = salt
        save_to_db(user, "User updated")

    @staticmethod
    def add_owner_to_event(owner_id, event):
        event.owner = owner_id
        db.session.commit()

    @staticmethod
    def create_event(form):
        """
        Event will be saved to database with proper Event id
        :param form: view data form
        """
        event = Event(name=form.name.data,
                      email=form.email.data,
                      color=form.color.data,
                      logo=form.logo.data,
                      start_time=form.start_time.data,
                      end_time=form.end_time.data,
                      latitude=form.latitude.data,
                      longitude=form.longitude.data,
                      location_name=form.location_name.data,
                      slogan=form.slogan.data,
                      url=form.url.data)
        a = EventsUsers()
        a.user = login.current_user
        a.editor = True
        a.admin = True
        event.users.append(a)
        if form.logo.data:
            event.logo = form.logo.data
        else:
            event.logo = ''
        save_to_db(event, "Event saved")
        update_version(event_id=event.id,
                       is_created=True,
                       column_to_increment="event_ver")

    @staticmethod
    def update_event(form, event):
        """
        Event will be updated in database
        :param form: view data form
        :param event: object contains all earlier data
        """
        data = form.data
        logo = data['logo']
        del data['logo']
        db.session.query(Event) \
            .filter_by(id=event.id) \
            .update(dict(data))
        if logo:
            event.logo = logo
        else:
            event.logo = ''
        save_to_db(event, "Event updated")
        update_version(event_id=event.id,
                       is_created=False,
                       column_to_increment="event_ver")

    @staticmethod
    def delete_event(e_id):
        EventsUsers.query.filter_by(event_id=e_id).delete()
        Event.query.filter_by(id=e_id).delete()
        db.session.commit()

    @staticmethod
    def create_file():
        """
        File from request will be saved to database
        """
        file = request.files["file"]
        filename = secure_filename(file.filename)
        if db.session.query(exists().where(File.name == filename)).scalar() == False:
            if file.mimetype.split('/', 1)[0] == "image":
                file.save(os.path.join(os.path.realpath('.') + '/static/', filename))
                file_object = File(name=filename, path='', owner_id=login.current_user.id)
                save_to_db(file_object, "file saved")
                flash("Image added")
            else:
                flash("The selected file is not an image. Please select a image file and try again.")
        else:
            flash("A file named \"" + filename + "\" already exists")

    @staticmethod
    def remove_file(file_id):
        """
        File from request will be removed from database
        """
        file = File.query.get(file_id)
        os.remove(os.path.join(os.path.realpath('.') + '/static/', file.name))
        delete_from_db(file, "File removed")
        flash("File removed")


def save_to_db(item, msg):
    """Convenience function to wrap a proper DB save
    :param item: will be saved to database
    :param msg: Message to log
    """
    try:
        logging.info(msg)
        db.session.add(item)
        logging.info('added to session')
        db.session.commit()
        return True
    except Exception, e:
        logging.error('DB Exception! %s' % e)
        traceback.print_exc()
        db.session.rollback()
        return False


def delete_from_db(item, msg):
    """Convenience function to wrap a proper DB delete
    :param item: will be removed from database
    :param msg: Message to log
    """
    try:
        logging.info(msg)
        db.session.delete(item)
        logging.info('removed from session')
        db.session.commit()
        return True
    except Exception, e:
        logging.error('DB Exception! %s' % e)
        db.session.rollback()
        return False


def update_version(event_id, is_created, column_to_increment):
    """Function resposnible for increasing version when some data will be created or changed
    :param event_id: Event id
    :param is_created: Object exist True/False
    :param column_to_increment: which column should be increment
    """
    VersionUpdater(event_id=event_id,
                   is_created=is_created,
                   column_to_increment=column_to_increment).update()


def get_or_create(model, **kwargs):
    instance = db.session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance
