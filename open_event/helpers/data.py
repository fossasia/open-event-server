"""Copyright 2015 Rafal Kowalski"""
import logging
import os.path
import random
import traceback
import json
from datetime import datetime, timedelta

from flask import flash, request, url_for, g
from flask.ext import login
from flask.ext.scrypt import generate_password_hash, generate_random_salt
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.sql.expression import exists
from werkzeug import secure_filename
from wtforms import ValidationError

from open_event.helpers.helpers import string_empty, send_new_session_organizer
from ..helpers.update_version import VersionUpdater
from ..helpers.data_getter import DataGetter
from open_event.helpers.storage import upload
from ..helpers import helpers as Helper
from ..models import db
from ..models.event import Event, EventsUsers
from ..models.file import File
from ..models.microlocation import Microlocation
from ..models.session import Session
from ..models.speaker import Speaker
from ..models.sponsor import Sponsor
from ..models.user import User, ORGANIZER
from ..models.user_detail import UserDetail
from ..models.role import Role
from ..models.service import Service
from ..models.permission import Permission
from ..models.users_events_roles import UsersEventsRoles
from ..models.session_type import SessionType
from ..models.social_link import SocialLink
from ..models.track import Track
from open_event.helpers.oauth import OAuth, FbOAuth
from requests_oauthlib import OAuth2Session
from ..models.invite import Invite
from ..models.call_for_papers import CallForPaper
from ..models.custom_forms import CustomForms
from ..models.activity import Activity, ACTIVITIES


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
        :param slide_file:
        :param event_id: Session belongs to Event by event id
        """
        new_session = Session(title=form.title.data,
                              subtitle=form.subtitle.data,
                              long_abstract=form.long_abstract.data,
                              start_time=form.start_time.data,
                              end_time=form.end_time.data,
                              event_id=event_id,
                              short_abstract=form.short_abstract.data)

        new_session.speakers = InstrumentedList(
            form.speakers.data if form.speakers.data else [])
        new_session.microlocation = form.microlocation.data
        new_session.track = form.track.data
        save_to_db(new_session, "Session saved")
        update_version(event_id, False, "session_ver")

    @staticmethod
    def add_session_to_event(request, event_id, state=None):
        """
        Session will be saved to database with proper Event id
        :param state:
        :param request: The request
        :param event_id: Session belongs to Event by event id
        """
        form = request.form
        speaker_img_file = ""
        slide_file = ""
        video_file = ""
        audio_file = ""
        if 'slides' in request.files and request.files['slides'].filename != '':
            slide_file = request.files['slides']
        if 'video' in request.files and request.files['video'].filename != '':
            video_file = request.files['video']
        if 'audio' in request.files and request.files['audio'].filename != '':
            audio_file = request.files['audio']
        if 'photo' in request.files and request.files['photo'].filename != '':
            speaker_img_file = request.files['photo']

        if not state:
            state = form.get('state', 'draft')

        event = DataGetter.get_event(event_id)

        new_session = Session(title=form.get('title', ''),
                              subtitle=form.get('subtitle', ''),
                              long_abstract=form.get('long_abstract', ''),
                              start_time=event.start_time,
                              end_time=event.start_time + timedelta(hours=1),
                              event_id=event_id,
                              short_abstract=form.get('short_abstract', ''),
                              state=state)

        speaker = Speaker.query.filter_by(email=form.get('email', '')).filter_by(event_id=event_id).first()
        if not speaker:
            speaker = Speaker(name=form.get('name', ''),
                              short_biography=form.get('short_biography', ''),
                              email=form.get('email', ''),
                              website=form.get('website', ''),
                              event_id=event_id,
                              twitter=form.get('twitter', ''),
                              facebook=form.get('facebook', ''),
                              github=form.get('github', ''),
                              linkedin=form.get('linkedin', ''),
                              organisation=form.get('organisation', ''),
                              position=form.get('position', ''),
                              country=form.get('country', ''),
                              user=login.current_user if login and login.current_user.is_authenticated else None)

        new_session.speakers.append(speaker)

        existing_speaker_ids = form.getlist("speakers[]")
        for existing_speaker_id in existing_speaker_ids:
            existing_speaker = DataGetter.get_speaker(existing_speaker_id)
            new_session.speakers.append(existing_speaker)

        save_to_db(new_session, "Session saved")

        if state == 'pending':
            link = url_for('event_sessions.session_display_view',
                           event_id=event.id, session_id=new_session.id, _external=True)
            organizers = DataGetter.get_user_event_roles_by_role_name(event.id, 'organizer')
            for organizer in organizers:
                send_new_session_organizer(organizer.user.email, event.name, link)

        slide_url = ""
        if slide_file != "":
            slide_url = upload(slide_file,
                               'events/%d/session/%d/slide' % (int(event_id), int(new_session.id)))
        audio_url = ""
        if audio_file != "":
            audio_url = upload(audio_file,
                               'events/%d/session/%d/audio' % (int(event_id), int(new_session.id)))
        video_url = ""
        if video_file != "":
            video_url = upload(video_file,
                               'events/%d/session/%d/video' % (int(event_id), int(new_session.id)))
        speaker_img = ""
        if speaker_img_file != "":
            speaker_img = upload(speaker_img_file,
                                 'events/%d/speaker/%d/photo' % (int(event_id), int(speaker.id)))

        speaker.photo = speaker_img
        new_session.audio = audio_url
        new_session.video = video_url
        new_session.slides = slide_url
        save_to_db(new_session, "Session saved")
        save_to_db(speaker, "Speaker saved")
        record_activity('create_session', session=new_session, event_id=event_id)

        invite_emails = form.getlist("speakers[email]")
        for index, email in enumerate(invite_emails):
            new_invite = Invite(event_id=event_id,
                                session_id=new_session.id)
            hash = random.getrandbits(128)
            new_invite.hash = "%032x" % hash
            save_to_db(new_invite, "Invite saved")

            link = url_for('event_sessions.invited_view', session_id=new_session.id, event_id=event_id, _external=True)
            Helper.send_email_invitation(email, new_session.title, link)

    @staticmethod
    def add_speaker_to_event(request, event_id, user=login.current_user):
        form = request.form
        speaker_img_file = ""
        if 'photo' in request.files and request.files['photo'].filename != '':
            speaker_img_file = request.files['photo']

        speaker = Speaker.query.filter_by(email=form.get('email', '')).filter_by(event_id=event_id).first()
        if not speaker:
            speaker = Speaker(name=form.get('name', ''),
                              short_biography=form.get('short_biography', ''),
                              email=form.get('email', ''),
                              website=form.get('website', ''),
                              event_id=event_id,
                              twitter=form.get('twitter', ''),
                              facebook=form.get('facebook', ''),
                              github=form.get('github', ''),
                              linkedin=form.get('linkedin', ''),
                              organisation=form.get('organisation', ''),
                              position=form.get('position', ''),
                              country=form.get('country', ''),
                              user=user if login and login.current_user.is_authenticated else None)
            save_to_db(speaker, "Speaker saved")

        speaker_img = ""
        if speaker_img_file != "":
            speaker_img = upload(speaker_img_file,
                                 'events/%d/speaker/%d/photo' % (int(event_id), int(speaker.id)))
            speaker.photo = speaker_img
            save_to_db(speaker, "Speaker photo saved")

        return speaker

    @staticmethod
    def add_speaker_to_session(request, event_id, session_id, user=login.current_user):
        """
        Session will be saved to database with proper Event id
        :param session_id:
        :param user:
        :param request: view data form
        :param event_id: Session belongs to Event by event id
        """
        session = DataGetter.get_session(session_id)
        speaker = DataManager.add_speaker_to_event(request, event_id, user)
        session.speakers.append(speaker)
        save_to_db(session, "Speaker saved")
        update_version(event_id, False, "speakers_ver")

    @staticmethod
    def create_speaker_session_relation(session_id, speaker_id, event_id):
        """
        Session, speaker ids will be saved to database
        :param speaker_id:
        :param session_id:
        :param event_id: Session, speaker belongs to Event by event id
        """
        speaker = DataGetter.get_speaker(speaker_id)
        session = DataGetter.get_session(session_id)
        session.speakers.append(speaker)
        save_to_db(session, "Session Speaker saved")

    @staticmethod
    def edit_session(request, session):
        form = request.form
        event_id = session.event_id

        slide_file = ""
        video_file = ""
        audio_file = ""
        if 'slides' in request.files and request.files['slides'].filename != '':
            slide_file = request.files['slides']
        if 'video' in request.files and request.files['video'].filename != '':
            video_file = request.files['video']
        if 'audio' in request.files and request.files['audio'].filename != '':
            audio_file = request.files['audio']

        form_state = form.get('state', 'draft')

        if slide_file != "":
            slide_url = upload(slide_file,
                               'events/%d/session/%d/slide' % (int(event_id), int(session.id)))
            session.slides = slide_url

        if audio_file != "":
            audio_url = upload(audio_file,
                               'events/%d/session/%d/audio' % (int(event_id), int(session.id)))
            session.audio = audio_url
        if video_file != "":
            video_url = upload(video_file,
                               'events/%d/session/%d/video' % (int(event_id), int(session.id)))
            session.video = video_url

        if form_state == 'pending' and session.state != 'pending' and session.state != 'accepted' and session.state != 'rejected':
            link = url_for('event_sessions.session_display_view',
                           event_id=event_id, session_id=session.id, _external=True)
            organizers = DataGetter.get_user_event_roles_by_role_name(event_id, 'organizer')
            for organizer in organizers:
                send_new_session_organizer(organizer.user.email, session.event.name, link)
            session.state = form_state

        session.title = form.get('title', '')
        session.subtitle = form.get('subtitle', '')
        session.long_abstract = form.get('long_abstract', '')
        session.short_abstract = form.get('short_abstract', '')

        existing_speaker_ids = form.getlist("speakers[]")

        session.speakers = []

        for existing_speaker_id in existing_speaker_ids:
            existing_speaker = DataGetter.get_speaker(existing_speaker_id)
            session.speakers.append(existing_speaker)

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
        track = data["track"]
        del data["speakers"]
        del data["microlocation"]
        del data["track"]
        db.session.query(Session) \
            .filter_by(id=session.id) \
            .update(dict(data))
        session.speakers = InstrumentedList(speakers if speakers else [])
        session.microlocation = microlocation
        session.track = track
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
    def create_speaker(form, event_id, user=login.current_user):
        """
        Speaker will be saved to database with proper Event id
        :param user:
        :param form: view data form
        :param event_id: Speaker belongs to Event by event id
        """
        speaker = Speaker(name=form["name"] if "name" in form.keys() else "",
                          photo=form["photo"] if "photo" in form.keys() else "",
                          short_biography=form["short_biography"] if "short_biography" in form.keys() else "",
                          email=form["email"] if "email" in form.keys() else "",
                          website=form["website"] if "website" in form.keys() else "",
                          event_id=event_id,
                          twitter=form["twitter"] if "twitter" in form.keys() else "",
                          facebook=form["facebook"] if "facebook" in form.keys() else "",
                          github=form["github"] if "github" in form.keys() else "",
                          linkedin=form["linkedin"] if "linkedin" in form.keys() else "",
                          organisation=form["organisation"] if "organisation" in form.keys() else "",
                          position=form["position"] if "position" in form.keys() else "",
                          country=form["country"] if "country" in form.keys() else "",
                          user=user)
        save_to_db(speaker, "Speaker saved")
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
        record_activity('delete_role', role=uer.role, user=uer.user, event_id=uer.event_id)
        delete_from_db(uer, "UER deleted")
        flash('You successfully delete role')

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
    def create_user(userdata, is_verified=False):
        user = User(email=userdata[0],
                    password=userdata[1],
                    is_verified=is_verified)
        # we hash the users password to avoid saving it as plaintext in the db,
        # remove to use plain text:
        salt = generate_random_salt()
        user.password = generate_password_hash(user.password, salt)
        hash = random.getrandbits(128)
        user.reset_password = str(hash)

        user.salt = salt
        save_to_db(user, "User created")
        record_activity('create_user', user=user)

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
        user.is_super_admin = True
        user.is_admin = True
        user.is_verified = True
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
    def update_user(form, user_id, avatar_img):

        user = User.query.filter_by(id=user_id).first()
        user_detail = UserDetail.query.filter_by(user_id=user_id).first()

        user.email = form['email']
        user_detail.fullname = form['full_name']
        user_detail.facebook = form['facebook']
        user_detail.contact = form['contact']
        user_detail.twitter = form['twitter']
        user_detail.details = form['details']
        user_detail.avatar_uploaded = avatar_img
        print user, user_detail, save_to_db(user, "User updated")
        record_activity('update_user', user=user)

    @staticmethod
    def add_owner_to_event(owner_id, event):
        event.owner = owner_id
        db.session.commit()

    @staticmethod
    def update_permissions(form):
        oper = {
            'c': 'can_create',
            'r': 'can_read',
            'u': 'can_update',
            'd': 'can_delete',
        }
        for role in Role.query.all():
            for service in Service.query.all():
                field = role.name + '-' + service.name
                perm = Permission.query.filter_by(role=role, service=service).first()
                if not perm:
                    perm = Permission(role=role, service=service)

                for v, attr in oper.iteritems():
                    if v in form.getlist(field):
                        setattr(perm, oper[v], True)
                    else:
                        setattr(perm, oper[v], False)

                save_to_db(perm, 'Permission saved')

    @staticmethod
    def create_event(form, img_files):
        """
        Event will be saved to database with proper Event id
        :param form: view data form
        """
        event = Event(name=form['name'],
                      email='dsads',
                      color='#f5f5f5',
                      logo=form['logo'],
                      start_time=datetime.strptime(form['start_date'] + ' ' + form['start_time'], '%m/%d/%Y %H:%M'),
                      end_time=datetime.strptime(form['start_date'] + ' ' + form['end_time'], '%m/%d/%Y %H:%M'),
                      timezone=form['timezone'],
                      latitude=form['latitude'],
                      longitude=form['longitude'],
                      location_name=form['location_name'],
                      description=form['description'],
                      event_url=form['event_url'],
                      background_url=form['background_url'],
                      type=form['event_type'],
                      topic=form['topic'],
                      privacy=form.get('privacy', 'public'),
                      ticket_url=form['ticket_url'],
                      organizer_name=form['organizer_name'],
                      organizer_description=form['organizer_description'],
                      creator=login.current_user)

        state = form.get('state', None)
        if state and ((state == u'Published' and not string_empty(event.location_name)) or state != u'Published') and login.current_user.is_verified:
            event.state = state

        if event.start_time <= event.end_time:
            save_to_db(event, "Event Saved")
            record_activity('create_event', event_id=event.id)
            role = Role.query.filter_by(name=ORGANIZER).first()
            db.session.add(event)
            db.session.flush()
            db.session.refresh(event)

            session_type_names = form.getlist('session_type[name]')
            session_type_length = form.getlist('session_type[length]')

            social_link_name = form.getlist('social[name]')
            social_link_link = form.getlist('social[link]')

            track_name = form.getlist('tracks[name]')
            track_color = form.getlist('tracks[color]')

            room_name = form.getlist('rooms[name]')
            room_color = form.getlist('rooms[color]')

            sponsor_name = form.getlist('sponsors[name]')
            sponsor_url = form.getlist('sponsors[url]')
            sponsor_level = form.getlist('sponsors[level]')
            sponsor_description = form.getlist('sponsors[description]')
            sponsor_logo_url = []

            custom_forms_name = form.getlist('custom_form[name]')
            custom_forms_value = form.getlist('custom_form[value]')

            for index, name in enumerate(session_type_names):
                if not string_empty(name):
                    session_type = SessionType(name=name, length=session_type_length[index], event_id=event.id)
                    db.session.add(session_type)

            for index, name in enumerate(social_link_name):
                if not string_empty(social_link_link[index]):
                    social_link = SocialLink(name=name, link=social_link_link[index], event_id=event.id)
                    db.session.add(social_link)

            for index, name in enumerate(track_name):
                track = Track(name=name, description="", track_image_url="", color=track_color[index],
                              event_id=event.id)
                db.session.add(track)

            for index, name in enumerate(room_name):
                if not string_empty(name):
                    room = Microlocation(name=name, event_id=event.id)
                    db.session.add(room)

            for index, name in enumerate(sponsor_name):
                if not string_empty(name):
                    sponsor = Sponsor(name=name, url=sponsor_url[index],
                                      level=sponsor_level[index], description=sponsor_description[index],
                                      event_id=event.id)
                    save_to_db(sponsor, "Sponsor created")
                    if len(img_files) != 0:
                        img_url = upload(img_files[index],
                                         'events/%d/sponsor/%d/image' % (int(event.id), int(sponsor.id)))
                        sponsor_logo_url.append(img_url)
                        sponsor.logo = sponsor_logo_url[index]
                    else:
                        sponsor.logo = ""
                    save_to_db(sponsor, "Sponsor updated")

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

            if form.get('call_for_speakers_state', u'off') == u'on':
                call_for_speakers = CallForPaper(announcement=form['announcement'],
                                                 start_date=datetime.strptime(form['cfs_start_date'], '%m/%d/%Y'),
                                                 end_date=datetime.strptime(form['cfs_end_date'], '%m/%d/%Y'),
                                                 event_id=event.id)
                save_to_db(call_for_speakers, "Call for speakers saved")

            uer = UsersEventsRoles(login.current_user, event, role)
            if save_to_db(uer, "Event saved"):
                return event
        else:
            raise ValidationError("start date greater than end date")

    @staticmethod
    def edit_event(request, event_id, event, session_types, tracks, social_links, microlocations, call_for_papers,
                   sponsors, custom_forms):
        """
        Event will be updated in database
        :param data: view data form
        :param event: object contains all earlier data
        """
        form = request.form
        event.name = form['name']
        event.logo = form['logo']
        event.start_time = datetime.strptime(form['start_date'] + ' ' + form['start_time'], '%m/%d/%Y %H:%M')
        event.end_time = datetime.strptime(form['start_date'] + ' ' + form['end_time'], '%m/%d/%Y %H:%M')
        event.timezone = form['timezone']
        event.latitude = form['latitude']
        event.longitude = form['longitude']
        event.location_name = form['location_name']
        event.description = form['description']
        event.event_url = form['event_url']
        event.background_url = form['background_url']
        event.type = form['event_type']
        event.topic = form['topic']
        event.privacy = form.get('privacy', 'public')
        event.organizer_name = form['organizer_name']
        event.organizer_description = form['organizer_description']
        event.ticket_url = form['ticket_url']

        state = form.get('state', None)
        if state and ((state == u'Published' and not string_empty(event.location_name)) or state != u'Published') and login.current_user.is_verified:
            event.state = state

        session_type_names = form.getlist('session_type[name]')
        session_type_length = form.getlist('session_type[length]')

        social_link_name = form.getlist('social[name]')
        social_link_link = form.getlist('social[link]')

        track_name = form.getlist('tracks[name]')
        track_color = form.getlist('tracks[color]')

        room_name = form.getlist('rooms[name]')
        room_color = form.getlist('rooms[color]')

        sponsor_name = form.getlist('sponsors[name]')
        sponsor_logo = request.files.getlist('sponsors[logo]')
        sponsor_url = form.getlist('sponsors[url]')
        sponsor_type = form.getlist('sponsors[type]')
        sponsor_level = form.getlist('sponsors[level]')
        sponsor_description = form.getlist('sponsors[description]')

        custom_forms_name = form.getlist('custom_form[name]')
        custom_forms_value = form.getlist('custom_form[value]')

        # save the edited info to database
        for index, name in enumerate(session_type_names):
            if not string_empty(name):
                session_type, c = get_or_create(SessionType,
                                                name=name,
                                                length=session_type_length[index],
                                                event_id=event.id)
                db.session.add(session_type)

        for index, name in enumerate(social_link_name):
            if not string_empty(social_link_link[index]):
                social_link, c = get_or_create(SocialLink,
                                               name=name,
                                               link=social_link_link[index],
                                               event_id=event.id)
                db.session.add(social_link)

        for index, name in enumerate(track_name):
            if not string_empty(name):
                track, c = get_or_create(Track,
                                         name=name,
                                         color=track_color[index].upper(),
                                         event_id=event.id)
                db.session.add(track)

        for index, name in enumerate(room_name):
            if not string_empty(name):
                room, c = get_or_create(Microlocation, name=name, event_id=event.id)
                db.session.add(room)

        for index, name in enumerate(sponsor_name):
            if not string_empty(name):
                sponsor, c = get_or_create(Sponsor,
                                           name=name,
                                           logo=sponsor_logo[index].filename,
                                           url=sponsor_url[index],
                                           sponsor_type=sponsor_type[index],
                                           level=sponsor_level[index],
                                           description=sponsor_description[index],
                                           event_id=event.id)
                db.session.add(sponsor)

        session_form = ""
        speaker_form = ""
        for index, name in enumerate(custom_forms_name):
            print name
            if name == "session_form":
                session_form = custom_forms_value[index]
            elif name == "speaker_form":
                speaker_form = custom_forms_value[index]

        custom_form, c = get_or_create(CustomForms,
                                       session_form=session_form,
                                       speaker_form=speaker_form,
                                       event_id=event.id)
        db.session.add(custom_form)

        if form.get('call_for_speakers_state', u'off') == u'on':
            call_for_speakers, c = get_or_create(CallForPaper,
                                                 announcement=form['announcement'],
                                                 start_date=datetime.strptime(
                                                     form['cfs_start_date'], '%m/%d/%Y'),
                                                 end_date=datetime.strptime(
                                                     form['cfs_end_date'], '%m/%d/%Y'),
                                                 event_id=event.id)
            save_to_db(call_for_speakers)

        save_to_db(event, "Event saved")
        record_activity('update_event', event_id=event.id)
        return event

    @staticmethod
    def delete_event(e_id):
        EventsUsers.query.filter_by(event_id=e_id).delete()
        UsersEventsRoles.query.filter_by(event_id=e_id).delete()
        SessionType.query.filter_by(event_id=e_id).delete()
        SocialLink.query.filter_by(event_id=e_id).delete()
        Track.query.filter_by(id=e_id).delete()
        Event.query.filter_by(id=e_id).delete()
        record_activity('delete_event', event_id=e_id)
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
        user = User.query.filter_by(email=form['user_email']).first()
        role = Role.query.filter_by(name=form['user_role']).first()
        uer = UsersEventsRoles(event=Event.query.get(event_id),
                               user=user, role=role)
        save_to_db(uer, "Event saved")
        record_activity('create_role', role=role, user=user, event_id=event_id)

    @staticmethod
    def update_user_event_role(form, uer):
        role = Role.query.filter_by(name=form['user_role']).first()
        user = User.query.filter_by(email=form['user_email']).first()
        uer.user = user
        uer.role_id = role.id
        save_to_db(uer, "Event saved")
        record_activity('update_role', role=role, user=user, event_id=uer.event_id)


def save_to_db(item, msg="Saved to db"):
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
    if method == 'Google':
        user.avatar = user_data['picture']
    if method == 'Facebook':
        user.avatar = user_data['picture']['data']['url']
    user.tokens = json.dumps(token)
    user.is_verified = True
    save_to_db(user, "User created")
    return user


def create_user_password(form, user):
    salt = generate_random_salt()
    password = form['new_password_again']
    user.password = generate_password_hash(password, salt)
    hash = random.getrandbits(128)
    user.reset_password = str(hash)
    user.salt = salt
    user.is_verified = True
    save_to_db(user, "User password created")
    return user


def user_logged_in(user):
    speakers = DataGetter.get_speaker_by_email(user.email).all()
    for speaker in speakers:
        if not speaker.user:
            speaker.user = user
            role = Role.query.filter_by(name='speaker').first()
            event = DataGetter.get_event(speaker.event_id)
            uer = UsersEventsRoles(user=user, event=event, role=role)
            save_to_db(uer)
            save_to_db(speaker)
    return True


def record_activity(template, login_user=None, **kwargs):
    """
    record an activity
    """
    if not login_user and hasattr(g, 'user'):
        login_user = g.user
    if not login_user and login.current_user.is_authenticated:
        login_user = login.current_user
    if login_user:
        actor = login_user.email + ' (' + str(login_user.id) + ')'
    else:
        actor = 'Anonymous'
    id_str = ' (%d)'
    s = '"%s"'
    # add more information for objects
    for k in kwargs:
        v = kwargs[k]
        if k.startswith('user'):
            kwargs[k] = s % v.email + id_str % v.id
        elif k.startswith('role'):
            kwargs[k] = s % v.title_name
        elif k.startswith('session'):
            kwargs[k] = s % v.title + id_str % v.id
        else:
            kwargs[k] = str(v)
    msg = ACTIVITIES[template].format(**kwargs)
    # conn.execute(Activity.__table__.insert().values(
    #     actor=actor, action=msg, time=datetime.now()
    # ))
    activity = Activity(actor=actor, action=msg)
    save_to_db(activity, 'Activity Recorded')


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
    was_created = False
    instance = db.session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, was_created
    else:
        instance = model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        was_created = True
        return instance, was_created


def update_role_to_admin(form, user_id):
    user = DataGetter.get_user(user_id)
    if form['admin_perm'] == 'isAdmin':
        user.is_admin = True
    else:
        user.is_admin = False

    save_to_db(user, "User role Updated")
