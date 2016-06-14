"""Copyright 2015 Rafal Kowalski"""
import logging
import os.path
import random
import traceback
import json
from datetime import datetime

from flask import flash, request
from flask.ext import login
from flask.ext.scrypt import generate_password_hash, generate_random_salt
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.sql.expression import exists
from werkzeug import secure_filename
from wtforms import ValidationError

from ..helpers.update_version import VersionUpdater
from ..models import db
from ..models.event import Event, EventsUsers
from ..models.file import File
from ..models.microlocation import Microlocation
from ..models.session import Session, Level, Format, Language
from ..models.speaker import Speaker
from ..models.sponsor import Sponsor
from ..models.user import User
from ..models.user_detail import UserDetail
from ..models.role import Role
from ..models.users_events_roles import UsersEventsRoles
from ..models.session_type import SessionType
from ..models.sessions_speakers import SessionsSpeakers
from ..models.social_link import SocialLink
from ..models.track import Track
from open_event.helpers.oauth import OAuth, FbOAuth
from requests_oauthlib import OAuth2Session
from ..models.invite import Invite
from ..models.call_for_papers import CallForPaper
from ..models.custom_forms import CustomForms


class DataManager(object):
    """Main class responsible for DataBase managing"""

    @staticmethod
    def add_invite_to_event(user_id, event_id):
        """
        Invite will be saved to database with proper Event id and User id
        :param user_id: Invite belongs to User by user id
        :param event_id: Invite belongs to Event by event id
        """
        new_invite = Invite(user_id=user_id,
                            event_id=event_id)
        hash = random.getrandbits(128)
        new_invite.hash = "%032x" % hash
        save_to_db(new_invite, "Invite saved")

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
        save_to_db(new_track, "Track saved")
        update_version(event_id, False, "tracks_ver")

    @staticmethod
    def create_new_track(form, event_id):
        """
        Track will be saved to database with proper Event id
        :param form: view data form
        :param event_id: Track belongs to Event by event id
        """
        new_track = Track(name=form['name'],
                          description=form['description'],
                          event_id=event_id,
                          track_image_url=form['track_image_url'])
        save_to_db(new_track, "Track saved")

    @staticmethod
    def update_track(form, track):
        """
        Track will be updated in database
        :param form: view data form
        :param track: object contains all earlier data
        """
        data = form.data
        db.session.query(Track) \
            .filter_by(id=track.id) \
            .update(dict(data))
        save_to_db(track, "Track updated")
        update_version(track.event_id, False, "tracks_ver")

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

        new_session.speakers = InstrumentedList(
            form.speakers.data if form.speakers.data else [])
        new_session.microlocation = form.microlocation.data
        new_session.format = form.format.data
        new_session.level = form.level.data
        new_session.track = form.track.data
        new_session.is_accepted = is_accepted
        save_to_db(new_session, "Session saved")
        update_version(event_id, False, "session_ver")

    @staticmethod
    def add_session_to_event(form, event_id):
        """
        Session will be saved to database with proper Event id
        :param form: view data form
        :param event_id: Session belongs to Event by event id
        """
        new_session = Session(title=form["title"],
                              subtitle="",
                              description=form["description"],
                              start_time=form["start_time"],
                              end_time=form["end_time"],
                              event_id=event_id,
                              abstract="",
                              state="pending")

        save_to_db(new_session, "Session saved")
        update_version(event_id, False, "session_ver")

        new_speaker = Speaker(name=form["name"],
                              photo="",
                              biography=form["biography"],
                              email=form["email"],
                              web=form["web"],
                              event_id=event_id,
                              twitter="",
                              facebook="",
                              github="",
                              linkedin="",
                              organisation=form["organisation"],
                              position="",
                              country="")
        save_to_db(new_speaker, "Speaker saved")
        update_version(event_id, False, "speakers_ver")

        new_session_speaker = SessionsSpeakers(session_id=new_session.id,
                                               speaker_id=new_speaker.id)

        save_to_db(new_session_speaker, "Session Speaker saved")

    @staticmethod
    def create_speaker_session_relation(session_id, speaker_id, event_id):
        """
        Session, speaker ids will be saved to database
        :param form: view data form
        :param event_id: Session, speaker belongs to Event by event id
        """
        new_session_speaker = SessionsSpeakers(session_id=session_id,
                                               speaker_id=speaker_id)

        save_to_db(new_session_speaker, "Session Speaker saved")

    @staticmethod
    def edit_session(form, session):
        session.title = form['title']
        session.subtitle = form['subtitle']
        session.description = form['description']
        session.start_time = form['start_time']
        session.end_time = form['end_time']
        session.abstract = form['abstract']

        save_to_db(session, 'Session Updated')

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
        track = data["track"]
        language = data["language"]
        del data["speakers"]
        del data["microlocation"]
        del data["level"]
        del data["format"]
        del data["track"]
        del data["language"]
        db.session.query(Session) \
            .filter_by(id=session.id) \
            .update(dict(data))
        session.speakers = InstrumentedList(speakers if speakers else [])
        session.microlocation = microlocation
        session.format = format
        session.level = level
        session.track = track
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
        new_speaker = Speaker(name=form["name"],
                              photo="",
                              biography=form["biography"],
                              email=form["email"],
                              web=form["web"],
                              event_id=event_id,
                              twitter="",
                              facebook="",
                              github="",
                              linkedin="",
                              organisation=form["organisation"],
                              position="",
                              country="")
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
        speaker.sessions = InstrumentedList(
            form.sessions.data if form.sessions.data else [])
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
    def remove_role(uer_id):
        """
        Role will be removed from database
        :param uer_id: Role id to remove object
        """
        uer = UsersEventsRoles.query.get(uer_id)
        delete_from_db(uer, "UER deleted")
        flash('You successfully delete role')

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
    def create_user(userdata):
        user = User(email=userdata[0],
                    password=userdata[1])

        # we hash the users password to avoid saving it as plaintext in the db,
        # remove to use plain text:
        salt = generate_random_salt()
        user.password = generate_password_hash(user.password, salt)
        hash = random.getrandbits(128)
        user.reset_password = str(hash)

        user.salt = salt
        user.role = 'speaker'
        save_to_db(user, "User created")

        return user

    @staticmethod
    def create_super_admin(email, password):
        user = User()
        user.login = 'super_admin'
        user.email = email
        salt = generate_random_salt()
        password = password
        user.password = generate_password_hash(password, salt)
        hash = random.getrandbits(128)
        user.reset_password = str(hash)
        user.salt = salt
        user.role = 'super_admin'
        save_to_db(user, "User created")
        return user

    @staticmethod
    def reset_password(form, reset_hash):
        user = User.query.filter_by(reset_password=reset_hash).first()
        salt = generate_random_salt()
        password = form['new_password_again']
        user.password = generate_password_hash(password, salt)
        new_hash = random.getrandbits(128)
        user.reset_password = new_hash
        user.salt = salt
        save_to_db(user, "password resetted")

    @staticmethod
    def update_user(form, user_id):

        user = User.query.filter_by(id=user_id).first()
        user_detail = UserDetail.query.filter_by(user_id=user_id).first()

        user.email = form['email']
        user_detail.fullname = form['full_name']
        user_detail.facebook = form['facebook']
        user_detail.avatar = form['avatar']
        user_detail.contact = form['contact']
        user_detail.twitter = form['twitter']
        user_detail.details = form['details']
        print user, user_detail, save_to_db(user, "User updated")

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
        event = Event(name=form['name'],
                      email='dsads',
                      color='#f5f5f5',
                      logo=form['logo'],
                      start_time=datetime.strptime(form['start_time'], '%m/%d/%Y'),
                      end_time=datetime.strptime(form['end_time'], '%m/%d/%Y'),
                      latitude=form['latitude'],
                      longitude=form['longitude'],
                      location_name=form['location_name'],
                      description=form['description'],
                      event_url=form['event_url'],
                      background_url=form['background_url'])
        state = form.get('state', None)
        if state:
            event.state = state

        if event.start_time <= event.end_time:
            role = Role(name='ORGANIZER')
            db.session.add(event)
            db.session.add(role)
            db.session.flush()
            db.session.refresh(event)
            db.session.refresh(role)

            session_type_names = form.getlist('session_type[name]')
            session_type_length = form.getlist('session_type[length]')

            social_link_name = form.getlist('social[name]')
            social_link_link = form.getlist('social[link]')

            track_name = form.getlist('tracks[name]')
            track_color = form.getlist('tracks[color]')

            room_name = form.getlist('rooms[name]')
            room_color = form.getlist('rooms[color]')

            call_for_speakers = CallForPaper(announcement=form['announcement'],
                                             start_date=datetime.strptime(form['start_date'], '%m/%d/%Y'),
                                             end_date=datetime.strptime(form['end_date'], '%m/%d/%Y'),
                                             event_id=event.id)

            sponsor_name = form.getlist('sponsors[name]')
            sponsor_url = form.getlist('sponsors[url]')
            sponsor_level = form.getlist('sponsors[level]')
            sponsor_description = form.getlist('sponsors[description]')

            custom_forms_name = form.getlist('custom_form[name]')
            custom_forms_value = form.getlist('custom_form[value]')

            for index, name in enumerate(session_type_names):
                session_type = SessionType(name=name, length=session_type_length[index], event_id=event.id)
                db.session.add(session_type)

            for index, name in enumerate(social_link_name):
                social_link = SocialLink(name=name, link=social_link_link[index], event_id=event.id)
                db.session.add(social_link)

            for index, name in enumerate(track_name):
                track = Track(name=name, description="", track_image_url="", color=track_color[index],
                              event_id=event.id)
                db.session.add(track)

            for index, name in enumerate(room_name):
                room = Microlocation(name=name, event_id=event.id)
                db.session.add(room)

            for index, name in enumerate(sponsor_name):
                sponsor = Sponsor(name=name,url=sponsor_url[index],
                                  level=sponsor_level[index], description=sponsor_description[index], event_id=event.id)
                db.session.add(sponsor)

            session_form = ""
            speaker_form = ""
            for index, name in enumerate(custom_forms_name):
                print name
                if name == "session_form":
                    session_form = custom_forms_value[index]
                elif name == "speaker_form":
                    speaker_form = custom_forms_value[index]

            custom_form = CustomForms(session_form=session_form, speaker_form=speaker_form, event_id=event.id)
            db.session.add(custom_form)

            uer = UsersEventsRoles(event_id=event.id, user_id=login.current_user.id, role_id=role.id)
            if save_to_db(call_for_speakers, "Call for paper saved") and save_to_db(uer, "Event saved"):
                return event
        else:
            raise ValidationError("start date greater than end date")

    @staticmethod
    def edit_event(form, event_id, event, session_types, tracks, social_links, microlocations, call_for_papers,
                   sponsors):
        """
        Event will be updated in database
        :param data: view data form
        :param event: object contains all earlier data
        """
        event.name = form['name']
        event.logo = form['logo']
        event.start_time = form['start_time']
        event.end_time = form['end_time']
        event.latitude = form['latitude']
        event.longitude = form['longitude']
        event.location_name = form['location_name']
        event.description = form['description']
        event.event_url = form['event_url']
        event.background_url = form['background_url']

        state = form.get('state', None)
        if state:
            event.state = state

        for session_type in session_types:
            delete_from_db(session_type, 'Session Type Deleted')

        for track in tracks:
            delete_from_db(track, 'Track')

        for social_link in social_links:
            delete_from_db(social_link, 'Social Link Deleted')

        for microlocation in microlocations:
            delete_from_db(microlocation, 'Microlocation deleted')

        for sponsor in sponsors:
            delete_from_db(sponsor, 'Sponsor deleted')

        for call_for_paper in call_for_papers:
            delete_from_db(call_for_paper, 'Call for paper deleted')

        session_type_names = form.getlist('session_type[name]')
        session_type_length = form.getlist('session_type[length]')

        social_link_name = form.getlist('social[name]')
        social_link_link = form.getlist('social[link]')

        track_name = form.getlist('tracks[name]')
        track_color = form.getlist('tracks[color]')

        room_name = form.getlist('rooms[name]')
        room_color = form.getlist('rooms[color]')

        call_for_speakers = CallForPaper(announcement=form['announcement'],
                                         start_date=datetime.strptime(form['start_date'], '%m/%d/%Y'),
                                         end_date=datetime.strptime(form['end_date'], '%m/%d/%Y'),
                                         event_id=event.id)

        sponsor_name = form.getlist('sponsors[name]')
        sponsor_logo = form.getlist('sponsors[logo]')
        sponsor_url = form.getlist('sponsors[url]')
        sponsor_level = form.getlist('sponsors[level]')
        sponsor_description = form.getlist('sponsors[description]')

        # save the edited info to database
        for index, name in enumerate(session_type_names):
            session_type = SessionType(name=name, length=session_type_length[index], event_id=event.id)
            db.session.add(session_type)

        for index, name in enumerate(social_link_name):
            social_link = SocialLink(name=name, link=social_link_link[index], event_id=event.id)
            db.session.add(social_link)

        for index, name in enumerate(track_name):
            track = Track(name=name, description="", track_image_url="", color=track_color[index],
                          event_id=event.id)
            db.session.add(track)

        for index, name in enumerate(room_name):
            room = Microlocation(name=name, event_id=event.id)
            db.session.add(room)

        for index, name in enumerate(sponsor_name):
            sponsor = Sponsor(name=name, logo=sponsor_logo[index], url=sponsor_url[index], level=sponsor_level[index],
                              description=sponsor_description[index], event_id=event.id)
            db.session.add(sponsor)

        save_to_db(call_for_speakers, "Call for papers saved")

        return event

    @staticmethod
    def delete_event(e_id):
        EventsUsers.query.filter_by(event_id=e_id).delete()
        UsersEventsRoles.query.filter_by(event_id=e_id).delete()
        SessionType.query.filter_by(event_id=e_id).delete()
        SocialLink.query.filter_by(event_id=e_id).delete()
        Track.query.filter_by(id=e_id).delete()
        Event.query.filter_by(id=e_id).delete()
        db.session.commit()

    @staticmethod
    def create_file():
        """
        File from request will be saved to database
        """
        file = request.files["file"]
        filename = secure_filename(file.filename)
        if not db.session.query(exists() \
                                    .where(File.name == filename)).scalar():
            if file.mimetype.split('/', 1)[0] == "image":
                file.save(os.path.join(os.path.realpath('.')
                                       + '/static/', filename))
                file_object = File(
                    name=filename,
                    path='',
                    owner_id=login.current_user.id
                )
                save_to_db(file_object, "file saved")
                flash("Image added")
            else:
                flash("The selected file is not an image. Please select a " \
                      "image file and try again.")
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

    @staticmethod
    def add_role_to_event(form, event_id):
        role = Role(name=form['user_role'])
        db.session.add(role)
        db.session.flush()
        db.session.refresh(role)
        uer = UsersEventsRoles(event_id=event_id, user_id=form['user_id'], role_id=role.id)
        save_to_db(uer, "Event saved")

    @staticmethod
    def update_user_event_role(form, uer):
        role = Role(name=form['user_role'])
        db.session.add(role)
        db.session.flush()
        db.session.refresh(role)
        uer.user = User.query.get(int(form['user_id']))
        uer.role_id = role.id
        save_to_db(uer, "Event saved")


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
        print e
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
        print e
        logging.error('DB Exception! %s' % e)
        db.session.rollback()
        return False


def get_google_auth(state=None, token=None):
    if token:
        return OAuth2Session(OAuth.get_client_id(), token=token)
    if state:
        return OAuth2Session(OAuth.get_client_id(), state=state, scope=OAuth.SCOPE,
                             redirect_uri=OAuth.get_redirect_uri())
    oauth = OAuth2Session(OAuth.get_client_id(), scope=OAuth.SCOPE, redirect_uri=OAuth.get_redirect_uri())
    return oauth


def get_facebook_auth(state=None, token=None):
    if token:
        return OAuth2Session(FbOAuth.get_client_id(), token=token)
    if state:
        return OAuth2Session(FbOAuth.get_client_id(), state=state, scope=FbOAuth.SCOPE,
                             redirect_uri=FbOAuth.get_redirect_uri())
    oauth = OAuth2Session(FbOAuth.get_client_id(), scope=FbOAuth.SCOPE, redirect_uri=FbOAuth.get_redirect_uri())
    return oauth


def create_user_oauth(user, user_data, token, method):
    if user is None:
        user = User()
        user.email = user_data['email']
    user.role = 'speaker'
    if method == 'Google':
        user.avatar = user_data['picture']
    if method == 'Facebook':
        user.avatar = user_data['picture']['data']['url']
    user.tokens = json.dumps(token)
    save_to_db(user, "User created")

    return user


def update_version(event_id, is_created, column_to_increment):
    """Function resposnible for increasing version when some data will be
    created or changed
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
