"""Copyright 2015 Rafal Kowalski"""
import json
import logging
import os.path
import random
import traceback
import oauth2
import time
from os import path
from datetime import datetime, timedelta
import PIL
from PIL import Image
import shutil

import requests
from requests.exceptions import ConnectionError
from flask import flash, request, url_for, g, current_app
from flask_socketio import emit
from flask.ext import login
from flask.ext.scrypt import generate_password_hash, generate_random_salt
from requests_oauthlib import OAuth2Session
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.sql.expression import exists
from werkzeug import secure_filename
from wtforms import ValidationError

from app.helpers.cache import cache
from app.helpers.helpers import string_empty, string_not_empty, uploaded_file
from app.helpers.notification_email_triggers import trigger_new_session_notifications, \
    trigger_session_state_change_notifications
from app.helpers.oauth import OAuth, FbOAuth, InstagramOAuth, TwitterOAuth
from app.helpers.storage import upload, UPLOAD_PATHS, UploadedFile, download_file, upload_local
from app.models.notifications import Notification
from app.models.stripe_authorization import StripeAuthorization
from app.views.admin.super_admin.super_admin_base import PANEL_LIST
from ..helpers import helpers as Helper
from ..helpers.data_getter import DataGetter
from ..helpers.static import EVENT_LICENCES
from ..helpers.update_version import VersionUpdater, get_all_columns
from ..helpers.system_mails import MAILS
from ..models import db
from ..models.activity import Activity, ACTIVITIES
from ..models.call_for_papers import CallForPaper
from ..models.panel_permissions import PanelPermission
from ..models.custom_forms import CustomForms
from ..models.event import Event, EventsUsers
from ..models.event_copyright import EventCopyright
from ..models.file import File
from ..models.invite import Invite
from ..models.microlocation import Microlocation
from ..models.user_permissions import UserPermission
from ..models.permission import Permission
from ..models.role import Role
from ..models.role_invite import RoleInvite
from ..models.ticket import Ticket, TicketTag
from ..models.service import Service
from ..models.session import Session
from ..models.session_type import SessionType
from ..models.social_link import SocialLink
from ..models.speaker import Speaker
from ..models.sponsor import Sponsor
from ..models.track import Track
from ..models.user import User, ORGANIZER, ATTENDEE, SYS_ROLES_LIST
from ..models.user_detail import UserDetail
from ..models.users_events_roles import UsersEventsRoles
from ..models.page import Page
from ..models.modules import Module
from ..models.email_notifications import EmailNotification
from ..models.message_settings import MessageSettings
from ..models.tax import Tax


class DataManager(object):
    """Main class responsible for DataBase managing"""

    @staticmethod
    def create_user_notification(user, action, title, message):
        """
        Create a User Notification
        :param user: User object to send the notification to
        :param action: Action being performed
        :param title: The message title
        :param message: The message
        """
        notification = Notification(user=user,
                                    action=action,
                                    title=title,
                                    message=message,
                                    received_at=datetime.now())
        saved = save_to_db(notification, 'User notification saved')

        if saved:
            DataManager.push_user_notification(user)

    @staticmethod
    def push_user_notification(user):
        """
        Push user notification using websockets.
        """
        if not current_app.config.get('INTEGRATE_SOCKETIO', False):
            return False
        user_room = 'user_{}'.format(user.id)
        emit('notifs-response',
             {'meta': 'New notifications',
              'notif_count': user.get_unread_notif_count(),
              'notifs': user.get_unread_notifs(reverse=True)},
             room=user_room,
             namespace='/notifs')
        emit('notifpage-response',
             {'meta': 'New notifpage notifications',
              'notif': DataGetter.get_latest_notif(user)},
             room=user_room,
             namespace='/notifpage')

    @staticmethod
    def mark_user_notification_as_read(notification):
        """Mark a particular notification read.
        """
        notification.has_read = True
        save_to_db(notification, 'Mark notification as read')

    @staticmethod
    def mark_all_user_notification_as_read(user):
        """Mark all notifications for a User as read.
        """
        unread_notifs = Notification.query.filter_by(user=user,
                                                     has_read=False)

        for notif in unread_notifs:
            notif.has_read = True
            db.session.add(notif)

        db.session.commit()

    @staticmethod
    def add_event_role_invite(email, role_name, event_id):
        """
        Save an event role invite to database and return accept and decline links.
        :param email: Email for the invite
        :param role_name: Role name for the invite
        :param event_id: Event id
        """
        role = Role.query.filter_by(name=role_name).first()

        event = Event.query.get(event_id)
        role_invite = RoleInvite(email=email,
                                 event=event,
                                 role=role,
                                 create_time=datetime.now())

        hash = random.getrandbits(128)
        role_invite.hash = '%032x' % hash

        save_to_db(role_invite, "Role Invite saved")

        accept_link = url_for('events.user_role_invite',
                              event_id=event_id,
                              hash=role_invite.hash)
        decline_link = url_for('events.user_role_invite_decline',
                               event_id=event_id,
                               hash=role_invite.hash)

        return accept_link, decline_link

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
        record_activity('invite_user', event_id=event_id, user_id=user_id)

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
        record_activity('create_track', event_id=event_id, track=new_track)
        update_version(event_id, False, "tracks_ver")

    @staticmethod
    def toggle_email_notification_settings(user_id, value):
        """
        Settings will be toggled to database with proper User id
        """
        events = DataGetter.get_all_events()
        user = DataGetter.get_user(user_id)
        notification_ids = []
        for event in events:
            if user.is_speaker_at_event(event.id) or user.is_organizer(event.id):
                email_notification = DataGetter.get_email_notification_settings_by_event_id(user_id, event.id)
                if email_notification:
                    email_notification.next_event = value
                    email_notification.new_paper = value
                    email_notification.session_schedule = value
                    email_notification.session_accept_reject = value
                    save_to_db(email_notification, "EmailSettings Toggled")
                    notification_ids.append(email_notification.id)
                else:
                    new_email_notification_setting = EmailNotification(next_event=value,
                                                                       new_paper=value,
                                                                       session_schedule=value,
                                                                       session_accept_reject=value,
                                                                       user_id=user_id,
                                                                       event_id=event.id)
                    save_to_db(new_email_notification_setting, "EmailSetting Toggled")
                    notification_ids.append(new_email_notification_setting.id)
        return notification_ids

    @staticmethod
    def add_email_notification_settings(form, user_id, event_id):
        """
        Settings will be saved to database with proper Event id and User id
        :param form: view data form
        :param event_id: Settings belongs to Event by event id
        :param user_id: Settings belongs to User by user id
        """
        email_notification_setting = DataGetter.get_email_notification_settings_by_event_id(user_id, event_id)
        if email_notification_setting:
            email_notification_setting.next_event = int(form.get('next_event', 0))
            email_notification_setting.new_paper = int(form.get('new_paper', 0))
            email_notification_setting.session_schedule = int(form.get('session_schedule', 0))
            email_notification_setting.session_accept_reject = int(form.get('session_accept_reject', 0))

            save_to_db(email_notification_setting, "EmailSettings Updated")
        else:
            new_email_notification_setting = EmailNotification(next_event=int(form.get('next_event', 0)),
                                                               new_paper=int(form.get('new_paper', 0)),
                                                               session_schedule=int(form.get('session_schedule', 0)),
                                                               session_accept_reject=int(
                                                                   form.get('session_accept_reject', 0)),
                                                               user_id=user_id,
                                                               event_id=event_id)
            save_to_db(new_email_notification_setting, "EmailSetting Saved")

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
        record_activity('create_track', event_id=event_id, track=new_track)
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
        record_activity('update_track', event_id=track.event_id, track=track)
        update_version(track.event_id, False, "tracks_ver")

    @staticmethod
    def remove_track(track_id):
        """
        Track will be removed from database
        :param track_id: Track id to remove object
        """
        track = Track.query.get(track_id)
        delete_from_db(track, "Track deleted")
        record_activity('delete_track', event_id=track.event_id, track=track)
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
        record_activity('create_session', session=new_session, event_id=event_id)
        update_version(event_id, False, "sessions_ver")

    @staticmethod
    def add_session_to_event(request, event_id, state=None):
        """
        Session will be saved to database with proper Event id
        :param state:
        :param request: The request
        :param event_id: Session belongs to Event by event id
        """
        form = request.form
        slide_file = DataManager.get_files_from_request(request, 'slides')
        video_file = DataManager.get_files_from_request(request, 'video')
        audio_file = DataManager.get_files_from_request(request, 'audio')
        speaker_img_file = DataManager.get_files_from_request(request, 'photo')

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

        if form.get('track', None) != "":
            new_session.track_id = form.get('track', None)

        if form.get('session_type', None) != "":
            new_session.session_type_id = form.get('session_type', None)

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

        # existing_speaker_ids = form.getlist("speakers[]")
        # for existing_speaker_id in existing_speaker_ids:
        #     existing_speaker = DataGetter.get_speaker(existing_speaker_id)
        #     new_session.speakers.append(existing_speaker)

        save_to_db(new_session, "Session saved")

        if state == 'pending':
            trigger_new_session_notifications(new_session.id, event=event)

        speaker_modified = False
        session_modified = False
        if slide_file != "":
            slide_url = upload(
                slide_file,
                UPLOAD_PATHS['sessions']['slides'].format(
                    event_id=int(event_id), id=int(new_session.id)
                ))
            new_session.slides = slide_url
            session_modified = True
        if audio_file != "":
            audio_url = upload(
                audio_file,
                UPLOAD_PATHS['sessions']['audio'].format(
                    event_id=int(event_id), id=int(new_session.id)
                ))
            new_session.audio = audio_url
            session_modified = True
        if video_file != "":
            video_url = upload(
                video_file,
                UPLOAD_PATHS['sessions']['video'].format(
                    event_id=int(event_id), id=int(new_session.id)
                ))
            new_session.video = video_url
            session_modified = True
        if speaker_img_file != "":
            speaker_img = upload(
                speaker_img_file,
                UPLOAD_PATHS['speakers']['photo'].format(
                    event_id=int(event_id), id=int(speaker.id)
                ))
            speaker.photo = speaker_img
            speaker_modified = True

        if session_modified:
            save_to_db(new_session, "Session saved")
        if speaker_modified:
            save_to_db(speaker, "Speaker saved")
        record_activity('create_session', session=new_session, event_id=event_id)
        update_version(event_id, False, 'sessions_ver')

        invite_emails = form.getlist("speakers[email]")
        for index, email in enumerate(invite_emails):
            if not string_empty(email):
                new_invite = Invite(event_id=event_id,
                                    session_id=new_session.id)
                hash = random.getrandbits(128)
                new_invite.hash = "%032x" % hash
                save_to_db(new_invite, "Invite saved")

                link = url_for('event_sessions.invited_view', session_id=new_session.id, event_id=event_id,
                               _external=True)
                Helper.send_email_invitation(email, new_session.title, link)
                # If a user is registered by the email, send a notification as well
                user = DataGetter.get_user_by_email(email, no_flash=True)
                if user:
                    cfs_link = url_for('event_detail.display_event_cfs', identifier=event.identifier)
                    Helper.send_notif_invite_papers(user, event.name, cfs_link, link)

    @staticmethod
    def get_files_from_request(request, file_type):
        if file_type in request.files and request.files[file_type].filename != '':
            return request.files[file_type]
        return ""

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
            record_activity('create_speaker', speaker=speaker, event_id=event_id)
        speaker_img = ""
        if speaker_img_file != "":
            speaker_img = upload(
                speaker_img_file,
                UPLOAD_PATHS['speakers']['photo'].format(
                    event_id=int(event_id), id=int(speaker.id)
                ))
            speaker.photo = speaker_img
            save_to_db(speaker, "Speaker photo saved")
            record_activity('update_speaker', speaker=speaker, event_id=event_id)
        update_version(event_id, False, 'speakers_ver')
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
        record_activity('add_speaker_to_session', speaker=speaker, session=session, event_id=event_id)
        update_version(event_id, False, "speakers_ver")
        update_version(event_id, False, "sessions_ver")

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
        update_version(speaker.event_id, False, "speakers_ver")
        update_version(session.event_id, False, "sessions_ver")

    @staticmethod
    def session_accept_reject(session, event_id, state):
        session.state = state
        session.submission_date = datetime.now()
        session.submission_modifier = login.current_user.email
        save_to_db(session, 'Session State Updated')
        trigger_session_state_change_notifications(session, event_id)
        flash("The session has been %s" % state)

    @staticmethod
    def edit_session(request, session):
        with db.session.no_autoflush:
            form = request.form
            event_id = session.event_id

            slide_file = DataManager.get_files_from_request(request, 'slides')
            video_file = DataManager.get_files_from_request(request, 'video')
            audio_file = DataManager.get_files_from_request(request, 'audio')

            form_state = form.get('state', 'draft')

            if slide_file != "":
                slide_url = upload(
                    slide_file,
                    UPLOAD_PATHS['sessions']['slides'].format(
                        event_id=int(event_id), id=int(session.id)
                    ))
                session.slides = slide_url

            if audio_file != "":
                audio_url = upload(
                    audio_file,
                    UPLOAD_PATHS['sessions']['audio'].format(
                        event_id=int(event_id), id=int(session.id)
                    ))
                session.audio = audio_url
            if video_file != "":
                video_url = upload(
                    video_file,
                    UPLOAD_PATHS['sessions']['video'].format(
                        event_id=int(event_id), id=int(session.id)
                    ))
                session.video = video_url

            if form_state == 'pending' and session.state != 'pending' and session.state != 'accepted' and session.state != 'rejected':
                trigger_new_session_notifications(session.id, event_id=event_id)

            session.title = form.get('title', '')
            session.subtitle = form.get('subtitle', '')
            session.long_abstract = form.get('long_abstract', '')
            session.short_abstract = form.get('short_abstract', '')
            session.state = form_state

            if form.get('track', None) != "":
                session.track_id = form.get('track', None)
            else:
                session.track_id = None

            if form.get('session_type', None) != "":
                session.session_type_id = form.get('session_type', None)
            else:
                session.session_type_id = None

            existing_speaker_ids = form.getlist("speakers[]")
            current_speaker_ids = []
            existing_speaker_ids_by_email = []

            save_to_db(session, 'Session Updated')

            for existing_speaker in DataGetter.get_speaker_by_email(form.get("email")).all():
                existing_speaker_ids_by_email.append(str(existing_speaker.id))

            for current_speaker in session.speakers:
                current_speaker_ids.append(str(current_speaker.id))

            for current_speaker_id in current_speaker_ids:
                if current_speaker_id not in existing_speaker_ids and current_speaker_id not in existing_speaker_ids_by_email:
                    current_speaker = DataGetter.get_speaker(current_speaker_id)
                    session.speakers.remove(current_speaker)
                    db.session.commit()

            for existing_speaker_id in existing_speaker_ids:
                existing_speaker = DataGetter.get_speaker(existing_speaker_id)
                if existing_speaker not in session.speakers:
                    session.speakers.append(existing_speaker)
                    db.session.commit()

            record_activity('update_session', session=session, event_id=event_id)
            update_version(event_id, False, "sessions_ver")

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
        update_version(session.event_id, False, "sessions_ver")
        record_activity('update_session', session=session, event_id=session.event_id)

    @staticmethod
    def remove_session(session_id):
        """
        Session will be removed from database
        :param session_id: Session id to remove object
        """
        session = Session.query.get(session_id)
        delete_from_db(session, "Session deleted")
        flash('You successfully delete session')
        record_activity('delete_session', session=session, event_id=session.event_id)
        update_version(session.event_id, False, "sessions_ver")

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
        speaker.ensure_social_links()
        save_to_db(speaker, "Speaker updated")
        record_activity('update_speaker', speaker=speaker, event_id=speaker.event_id)
        update_version(speaker.event_id, False, "speakers_ver")

    @staticmethod
    def remove_speaker(speaker_id):
        """
        Speaker will be removed from database
        :param speaker_id: Speaker id to remove object
        """
        speaker = Speaker.query.get(speaker_id)
        delete_from_db(speaker, "Speaker deleted")
        record_activity('delete_speaker', speaker=speaker, event_id=speaker.event_id)
        update_version(speaker.event_id, False, "speakers_ver")
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
        flash("You've successfully deleted role.")

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
    def update_user(form, user_id, avatar_img, contacts_only_update=False):

        user = User.query.filter_by(id=user_id).first()
        user_detail = UserDetail.query.filter_by(user_id=user_id).first()

        if user.email != form['email']:
            record_activity('update_user_email',
                            user_id=user.id, old=user.email, new=form['email'])
        if user.email != form['email']:
            user.is_verified = False
            serializer = Helper.get_serializer()
            data = [form['email']]
            form_hash = serializer.dumps(data)
            link = url_for('admin.create_account_after_confirmation_view', hash=form_hash, _external=True)
            Helper.send_email_when_changes_email(user.email, form['email'])
            Helper.send_email_confirmation(form, link)
            user.email = form['email']

        user_detail.contact = form['contact']
        if not contacts_only_update:
            user_detail.firstname = form['firstname']
            user_detail.lastname = form['lastname']

            if form['facebook'] != 'https://www.facebook.com/':
                user_detail.facebook = form['facebook']
            else:
                user_detail.facebook = ''

            if form['twitter'] != 'https://twitter.com/':
                user_detail.twitter = form['twitter']
            else:
                user_detail.twitter = ''

            user_detail.details = form['details']
            logo = form.get('logo', None)
            if string_not_empty(logo) and logo:
                logo_file = uploaded_file(file_content=logo)
                logo = upload(logo_file, 'users/%d/avatar' % int(user_id))
                user_detail.avatar_uploaded = logo
        user, user_detail, save_to_db(user, "User updated")
        record_activity('update_user', user=user)

    @staticmethod
    def add_owner_to_event(owner_id, event):
        event.owner = owner_id
        db.session.commit()

    @staticmethod
    def update_user_permissions(form):
        for perm in UserPermission.query.all():
            ver_user = '{}-verified_user'.format(perm.name)
            unver_user = '{}-unverified_user'.format(perm.name)
            # anon_user = '{}-anonymous_user'.format(perm.name)
            perm.verified_user = True if form.get(ver_user) == 'on' else False
            perm.unverified_user = True if form.get(unver_user) == 'on' else False
            # perm.anonymous_user = True if form.get(anon_user) == 'on' else False

            db.session.add(perm)
        db.session.commit()

    @staticmethod
    def update_panel_permissions(form):
        for role in SYS_ROLES_LIST:
            for panel in PANEL_LIST:
                field_name = '{}-{}'.format(role, panel)
                field_val = form.get(field_name)
                perm, _ = get_or_create(PanelPermission, panel_name=panel,
                    role_name=role)

                perm.can_access = True if field_val == 'on' else False
                db.session.add(perm)
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
    def create_ticket_tags(tagnames_csv, event_id):
        """Returns list of `TicketTag` objects.
        """
        tag_list = []
        for tagname in tagnames_csv.split(','):
            tag, _ = get_or_create(TicketTag, name=tagname, event_id=event_id)
            tag_list.append(tag)

        return tag_list

    @staticmethod
    def create_event(form, img_files):
        """
        Event will be saved to database with proper Event id
        :param img_files:
        :param form: view data form
        """
        # Filter out Copyright info
        holder = form.get('organizer_name')
        # Current year
        year = datetime.now().year
        licence_name = form.get('copyright_licence')
        # Ignoring Licence long name, description and compact logo
        _, _, licence_url, logo, _ = EVENT_LICENCES.get(licence_name, ('',) * 5)

        copyright = EventCopyright(holder=holder,
                                   year=year,
                                   licence=licence_name,
                                   licence_url=licence_url,
                                   logo=logo)

        payment_currency = ''
        if form['payment_currency'] != '':
            payment_currency = form.get('payment_currency').split(' ')[0]

        paypal_email = ''
        event = Event(name=form['name'],
                      start_time=DataManager.get_event_time_field_format(form, 'start'),
                      end_time=DataManager.get_event_time_field_format(form, 'end'),
                      timezone=form['timezone'],
                      latitude=form['latitude'],
                      longitude=form['longitude'],
                      location_name=form['location_name'],
                      description=form['description'],
                      event_url=form['event_url'],
                      type=form['type'],
                      topic=form['topic'],
                      sub_topic=form['sub_topic'],
                      privacy=form.get('privacy', u'public'),
                      ticket_url=form.get('ticket_url', None),
                      copyright=copyright,
                      show_map=1 if form.get('show_map') == "on" else 0,
                      creator=login.current_user,
                      payment_country=form.get('payment_country', ''),
                      payment_currency=payment_currency,
                      paypal_email=paypal_email)

        event.pay_by_paypal = 'pay_by_paypal' in form
        event.pay_by_cheque = 'pay_by_cheque' in form
        event.pay_by_bank = 'pay_by_bank' in form
        event.pay_onsite = 'pay_onsite' in form
        event.pay_by_stripe = 'pay_by_stripe' in form

        if 'pay_by_paypal' in form:
            event.paypal_email = form.get('paypal_email')
        else:
            event.paypal_email = None

        event = DataManager.update_searchable_location_name(event)

        if form.get('organizer_state', u'off') == u'on':
            event.organizer_name = form['organizer_name']
            event.organizer_description = form['organizer_description']

        if form.get('coc_state', u'off') == u'on':
            event.code_of_conduct = form['code_of_conduct']

        state = form.get('state', None)
        if state and ((state == u'Published' and not string_empty(
            event.location_name)) or state != u'Published') and login.current_user.is_verified:
            event.state = state

        if event.start_time <= event.end_time:
            save_to_db(event, "Event Saved")
            record_activity('create_event', event_id=event.id)
            role = Role.query.filter_by(name=ORGANIZER).first()
            db.session.add(event)
            db.session.flush()
            db.session.refresh(event)

            background_url = ''
            background_thumbnail_url = ''
            temp_background = form['background_url']
            image_sizes = DataGetter.get_image_sizes()
            if temp_background:
                if temp_background.startswith('/serve_static'):
                    # Local file
                    filename = str(time.time()) + '.png'
                    filepath = path.realpath('.') + '/static' + temp_background[len('/serve_static'):]
                    background_file = UploadedFile(filepath, filename)
                else:
                    background_file = download_file(temp_background)
                background_url = upload(
                    background_file,
                    UPLOAD_PATHS['event']['background_url'].format(
                        event_id=event.id
                    ))

                temp_img_file = upload_local(background_file,
                                             'events/{event_id}/temp'.format(event_id=int(event.id)))
                temp_img_file = temp_img_file.replace('/serve_', '')

                basewidth = image_sizes.full_width
                img = Image.open(temp_img_file)
                wpercent = (basewidth / float(img.size[0]))
                hsize = int((float(img.size[1]) * float(wpercent)))
                img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
                img.save(temp_img_file)
                file_name = temp_img_file.rsplit('/', 1)[1]
                large_file = UploadedFile(file_path=temp_img_file, filename=file_name)
                background_large_url = upload(
                    large_file,
                    UPLOAD_PATHS['event']['large'].format(
                        event_id=int(event.id)
                    ))

                basewidth = image_sizes.thumbnail_width
                img = Image.open(temp_img_file)
                wpercent = (basewidth / float(img.size[0]))
                hsize = int((float(img.size[1]) * float(wpercent)))
                img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
                img.save(temp_img_file)
                file_name = temp_img_file.rsplit('/', 1)[1]
                thumbnail_file = UploadedFile(file_path=temp_img_file, filename=file_name)
                background_thumbnail_url = upload(
                    thumbnail_file,
                    UPLOAD_PATHS['event']['thumbnail'].format(
                        event_id=int(event.id)
                    ))

                basewidth = image_sizes.icon_width
                img = Image.open(temp_img_file)
                wpercent = (basewidth / float(img.size[0]))
                hsize = int((float(img.size[1]) * float(wpercent)))
                img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
                img.save(temp_img_file)
                file_name = temp_img_file.rsplit('/', 1)[1]
                icon_file = UploadedFile(file_path=temp_img_file, filename=file_name)
                background_icon_url = upload(
                    icon_file,
                    UPLOAD_PATHS['event']['icon'].format(
                        event_id=int(event.id)
                    ))
                shutil.rmtree(path='static/media/' + 'events/{event_id}/temp'.format(event_id=int(event.id)))

            event.background_url = background_url
            event.thumbnail = background_thumbnail_url
            event.large = background_large_url
            event.icon = background_icon_url

            logo = ''
            temp_logo = form['logo']
            if temp_logo:
                if temp_logo.startswith('/serve_static'):
                    # Local file
                    filename = str(time.time()) + '.png'
                    filepath = path.realpath('.') + '/static' + temp_logo[len('/serve_static'):]
                    logo_file = UploadedFile(filepath, filename)
                else:
                    logo_file = download_file(temp_logo)

                logo = upload(
                    logo_file,
                    UPLOAD_PATHS['event']['logo'].format(
                        event_id=event.id
                    ))
            event.logo = logo

            # Save Tickets
            module = DataGetter.get_module()
            if module and module.ticket_include:

                event.ticket_url = url_for('event_detail.display_event_tickets',
                                           identifier=event.identifier,
                                           _external=True)

                ticket_names = form.getlist('tickets[name]')
                ticket_types = form.getlist('tickets[type]')
                ticket_prices = form.getlist('tickets[price]')
                ticket_quantities = form.getlist('tickets[quantity]')
                ticket_descriptions = form.getlist('tickets[description]')
                ticket_sales_start_dates = form.getlist('tickets[sales_start_date]')
                ticket_sales_start_times = form.getlist('tickets[sales_start_time]')
                ticket_sales_end_dates = form.getlist('tickets[sales_end_date]')
                ticket_sales_end_times = form.getlist('tickets[sales_end_time]')
                ticket_min_orders = form.getlist('tickets[min_order]')
                ticket_max_orders = form.getlist('tickets[max_order]')
                ticket_tags =  form.getlist('tickets[tags]')

                for i, name in enumerate(ticket_names):
                    if name.strip():
                        ticket_prices[i] = ticket_prices[i] if ticket_prices[i] != '' else 0
                        ticket_quantities[i] = ticket_quantities[i] if ticket_quantities[i] != '' else 100
                        ticket_min_orders[i] = ticket_min_orders[i] if ticket_min_orders[i] != '' else 1
                        ticket_max_orders[i] = ticket_max_orders[i] if ticket_max_orders[i] != '' else 10

                        sales_start_str = '{} {}'.format(ticket_sales_start_dates[i],
                                                         ticket_sales_start_times[i])
                        sales_end_str = '{} {}'.format(ticket_sales_end_dates[i],
                                                       ticket_sales_end_times[i])

                        description_toggle = form.get('tickets_description_toggle_{}'.format(i), False)
                        description_toggle = True if description_toggle == 'on' else False

                        tag_list = DataManager.create_ticket_tags(ticket_tags[i], event.id)
                        ticket = Ticket(
                            name=name,
                            type=ticket_types[i],
                            sales_start=datetime.strptime(sales_start_str, '%m/%d/%Y %H:%M'),
                            sales_end=datetime.strptime(sales_end_str, '%m/%d/%Y %H:%M'),
                            description=ticket_descriptions[i],
                            description_toggle=description_toggle,
                            quantity=ticket_quantities[i],
                            price=int(ticket_prices[i]) if ticket_types[i] == 'paid' else 0,
                            min_order=ticket_min_orders[i],
                            max_order=ticket_max_orders[i],
                            tags=tag_list,
                            event=event
                        )

                        db.session.add(ticket)

            sponsor_name = form.getlist('sponsors[name]')
            sponsor_url = form.getlist('sponsors[url]')
            sponsor_level = form.getlist('sponsors[level]')
            sponsor_description = form.getlist('sponsors[description]')
            sponsor_logo_url = []

            if 'pay_by_stripe' in form:
                if form.get('stripe_added', u'no') == u'yes':
                    stripe_authorization = StripeAuthorization(
                        stripe_secret_key=form.get('stripe_secret_key', ''),
                        stripe_refresh_token=form.get('stripe_refresh_token', ''),
                        stripe_publishable_key=form.get('stripe_publishable_key', ''),
                        stripe_user_id=form.get('stripe_user_id', ''),
                        stripe_email=form.get('stripe_email', ''),
                        event_id=event.id
                    )
                    save_to_db(stripe_authorization)

            if form.get('sponsors_state', u'off') == u'on':
                for index, name in enumerate(sponsor_name):
                    if not string_empty(name):
                        sponsor = Sponsor(name=name, url=sponsor_url[index],
                                          level=sponsor_level[index], description=sponsor_description[index],
                                          event_id=event.id)
                        save_to_db(sponsor, "Sponsor created")
                        if len(img_files) != 0:
                            img_url = upload(
                                img_files[index],
                                UPLOAD_PATHS['sponsors']['logo'].format(
                                    event_id=int(event.id), id=int(sponsor.id)
                                ))
                            sponsor_logo_url.append(img_url)
                            sponsor.logo = sponsor_logo_url[index]
                        else:
                            sponsor.logo = ""
                        save_to_db(sponsor, "Sponsor updated")

            social_link_name = form.getlist('social[name]')
            social_link_link = form.getlist('social[link]')

            for index, name in enumerate(social_link_name):
                if not string_empty(social_link_link[index]):
                    # If 'Website' has been provided,
                    # save it as Holder URL for Copyright
                    if name.lower() == 'website':
                        event.copyright.holder_url = social_link_link[index]
                    social_link = SocialLink(name=name, link=social_link_link[index], event_id=event.id)
                    db.session.add(social_link)

            event.has_session_speakers = False
            if form.get('has_session_speakers', u'no') == u'yes':
                event.has_session_speakers = True
                session_type_names = form.getlist('session_type[name]')
                session_type_length = form.getlist('session_type[length]')

                track_name = form.getlist('tracks[name]')
                track_color = form.getlist('tracks[color]')
                if len(track_name) == 0:
                    track_name.append("Main Track")
                    track_color.append("#ffffff")

                room_name = form.getlist('rooms[name]')
                room_floor = form.getlist('rooms[floor]')

                for index, name in enumerate(session_type_names):
                    if not string_empty(name):
                        session_type = SessionType(name=name, length=session_type_length[index], event_id=event.id)
                        db.session.add(session_type)

                for index, name in enumerate(track_name):
                    track = Track(name=name, description="", track_image_url="", color=track_color[index],
                                  event_id=event.id)
                    db.session.add(track)

                for index, name in enumerate(room_name):
                    if not string_empty(name):
                        room = Microlocation(name=name,
                                             floor=room_floor[index] if room_floor[index] != '' else None,
                                             event_id=event.id)
                        db.session.add(room)

                call_for_speakers = CallForPaper(announcement=form['announcement'],
                                                 start_date=datetime.strptime(form['cfs_start_date'] + ' ' +
                                                                              form['cfs_start_time'], '%m/%d/%Y %H:%M'),
                                                 end_date=datetime.strptime(form['cfs_end_date'] + ' ' +
                                                                            form['cfs_end_time'], '%m/%d/%Y %H:%M'),
                                                 timezone=form.get('cfs_timezone', 'UTC'),
                                                 hash=form['cfs_hash'],
                                                 privacy=form['cfs_privacy'],
                                                 event_id=event.id)
                save_to_db(call_for_speakers, "Call for speakers saved")

            custom_forms_name = form.getlist('custom_form[name]')
            custom_forms_value = form.getlist('custom_form[value]')

            session_form = ""
            speaker_form = ""
            for index, name in enumerate(custom_forms_name):
                print name
                if name == "session_form":
                    session_form = custom_forms_value[index]
                elif name == "speaker_form":
                    speaker_form = custom_forms_value[index]

            update_or_create(
                CustomForms, event_id=event.id,
                session_form=session_form, speaker_form=speaker_form)

            if module and (module.payment_include or module.donation_include) \
                and ('paid' or 'donation') in form.getlist('tickets[type]'):

                if form['taxAllow'] == 'taxNo':
                    event.tax_allow = False

                if form['taxAllow'] == 'taxYes':
                    event.tax_allow = True

                    tax_invoice = False
                    if 'tax_invoice' in form:
                        tax_invoice = True

                    tax_include_in_price = False
                    if form['tax_options'] == 'tax_include':
                        tax_include_in_price = True

                    tax = Tax(country=form['tax_country'],
                              tax_name=form['tax_name'],
                              tax_rate=form['tax_rate'],
                              tax_id=form['tax_id'],
                              send_invoice=tax_invoice,
                              registered_company=form.get('registered_company', ''),
                              address=form.get('buisness_address', ''),
                              city=form.get('invoice_city', ''),
                              state=form.get('invoice_state', ''),
                              zip=form.get('invoice_zip', 0),
                              invoice_footer=form.get('invoice_footer', ''),
                              tax_include_in_price=tax_include_in_price,
                              event_id=event.id)

                    save_to_db(tax, "Tax Options Saved")

            uer = UsersEventsRoles(login.current_user, event, role)

            if save_to_db(uer, "Event saved"):
                # Save event notification setting
                new_email_notification_setting = EmailNotification(next_event=1,
                                                                   new_paper=1,
                                                                   session_schedule=1,
                                                                   session_accept_reject=1,
                                                                   user_id=login.current_user.id,
                                                                   event_id=event.id)
                save_to_db(new_email_notification_setting, "EmailSetting Saved")
                return event
        else:
            raise ValidationError("start date greater than end date")

    @staticmethod
    def get_event_time_field_format(form, field):
        return datetime.strptime(form[field + '_date'] + ' ' + form[field + '_time'], '%m/%d/%Y %H:%M')

    @staticmethod
    def update_searchable_location_name(event):
        if event.latitude and event.longitude:
            url = 'https://maps.googleapis.com/maps/api/geocode/json'
            latlng = '{},{}'.format(event.latitude, event.longitude)
            params = {'latlng': latlng}
            response = dict()

            try:
                response = requests.get(url, params).json()
            except ConnectionError:
                response['status'] = u'Error'

            if response['status'] == u'OK':
                for addr in response['results'][0]['address_components']:
                    if addr['types'] == ['locality', 'political']:
                        event.searchable_location_name = addr['short_name']
        return event

    @staticmethod
    def create_event_copy(event_id):

        event_old = DataGetter.get_event(event_id)
        event = Event(name='Copy of ' + event_old.name,
                      start_time=event_old.start_time,
                      end_time=event_old.end_time,
                      timezone=event_old.timezone,
                      latitude=event_old.latitude,
                      longitude=event_old.longitude,
                      location_name=event_old.location_name,
                      description=event_old.description,
                      event_url=event_old.event_url,
                      type=event_old.type,
                      topic=event_old.topic,
                      sub_topic=event_old.sub_topic,
                      privacy=event_old.privacy,
                      ticket_url=None,
                      show_map=event_old.show_map,
                      organizer_name=event_old.organizer_name,
                      organizer_description=event_old.organizer_description)

        event.state = u'Draft'
        save_to_db(event, "Event copy saved")

        sponsors_old = DataGetter.get_sponsors(event_id)
        tracks_old = DataGetter.get_tracks(event_id)
        rooms_old = DataGetter.get_microlocations(event_id)
        call_for_papers_old = DataGetter.get_call_for_papers(event_id)

        for sponsor in sponsors_old:
            sponsor_new = Sponsor(name=sponsor.name, url=sponsor.url,
                                  level=sponsor.level, description=sponsor.description,
                                  event_id=event.id)
            save_to_db(sponsor_new, "Sponsor copy saved")

        for track in tracks_old:
            track_new = Track(name=track.name, description="", track_image_url="", color=track.color,
                              event_id=event.id)
            save_to_db(track_new, "Track copy saved")

        for room in rooms_old:
            room_new = Microlocation(name=room.name, floor=room.floor, event_id=event.id)
            save_to_db(room_new, "Room copy saved")

        if call_for_papers_old:
            for call_for_paper in call_for_papers_old:
                call_for_paper_new = CallForPaper(announcement=call_for_paper.announcement,
                                                  start_date=call_for_paper.start_date,
                                                  end_date=call_for_paper.end_date,
                                                  timezone=call_for_paper.timezone,
                                                  event_id=event.id)
                save_to_db(call_for_paper_new, "Call for speaker copy saved")

        return event

    @staticmethod
    def edit_event(request, event_id, event, session_types, tracks, social_links, microlocations, call_for_papers,
                   sponsors, custom_forms, img_files, old_sponsor_logos, old_sponsor_names, tax):
        """
        Event will be updated in database
        :param call_for_papers:
        :param tax:
        :param old_sponsor_names:
        :param microlocations:
        :param social_links:
        :param tracks:
        :param session_types:
        :param event_id:
        :param request:
        :param sponsors:
        :param custom_forms:
        :param img_files:
        :param old_sponsor_logos:
        :param event: object contains all earlier data
        """
        form = request.form
        event.name = form['name']
        event.start_time = DataManager.get_event_time_field_format(form, 'start')
        event.end_time = DataManager.get_event_time_field_format(form, 'end')
        event.timezone = form['timezone']
        event.latitude = form['latitude']
        event.longitude = form['longitude']
        event.location_name = form['location_name']
        event.description = form['description']
        event.event_url = form['event_url']
        event.type = form['type']
        event.topic = form['topic']
        event.show_map = 1 if form.get('show_map') == 'on' else 0
        event.sub_topic = form['sub_topic']
        event.privacy = form.get('privacy', 'public')
        event.payment_country = form.get('payment_country')

        event.pay_by_paypal = 'pay_by_paypal' in form
        event.pay_by_cheque = 'pay_by_cheque' in form
        event.pay_by_bank = 'pay_by_bank' in form
        event.pay_onsite = 'pay_onsite' in form
        event.pay_by_stripe = 'pay_by_stripe' in form

        if 'pay_by_paypal' in form:
            event.paypal_email = form.get('paypal_email')
        else:
            event.paypal_email = None

        payment_currency = ''
        if form['payment_currency'] != '':
            payment_currency = form.get('payment_currency').split(' ')[0]

        event.payment_currency = payment_currency
        event.paypal_email = form.get('paypal_email')

        ticket_names = form.getlist('tickets[name]')
        ticket_types = form.getlist('tickets[type]')
        ticket_prices = form.getlist('tickets[price]')
        ticket_quantities = form.getlist('tickets[quantity]')
        ticket_descriptions = form.getlist('tickets[description]')
        ticket_sales_start_dates = form.getlist('tickets[sales_start_date]')
        ticket_sales_start_times = form.getlist('tickets[sales_start_time]')
        ticket_sales_end_dates = form.getlist('tickets[sales_end_date]')
        ticket_sales_end_times = form.getlist('tickets[sales_end_time]')
        ticket_min_orders = form.getlist('tickets[min_order]')
        ticket_max_orders = form.getlist('tickets[max_order]')
        ticket_tags = form.getlist('tickets[tags]')

        for i, name in enumerate(ticket_names):
            if name.strip():
                ticket_prices[i] = ticket_prices[i] if ticket_prices[i] != '' else 0
                ticket_quantities[i] = ticket_quantities[i] if ticket_quantities[i] != '' else 100
                ticket_min_orders[i] = ticket_min_orders[i] if ticket_min_orders[i] != '' else 1
                ticket_max_orders[i] = ticket_max_orders[i] if ticket_max_orders[i] != '' else 10

                sales_start_str = '{} {}'.format(ticket_sales_start_dates[i],
                                                 ticket_sales_start_times[i])
                sales_end_str = '{} {}'.format(ticket_sales_end_dates[i],
                                               ticket_sales_end_times[i])

                hide = form.get('tickets_hide_{}'.format(i), False)
                hide = True if hide == 'on' else False

                description_toggle = form.get('tickets_description_toggle_{}'.format(i), False)
                description_toggle = True if description_toggle == 'on' else False

                tag_list = DataManager.create_ticket_tags(ticket_tags[i], event.id,)

                ticket, _ = get_or_create(Ticket, name=name, event=event, type=ticket_types[i])

                if not ticket.has_order_tickets():
                    ticket.price = int(ticket_prices[i]) if ticket_types[i] == 'paid' else 0
                    ticket.type = ticket_types[i]
                ticket.sales_start = datetime.strptime(sales_start_str, '%m/%d/%Y %H:%M')
                ticket.sales_end = datetime.strptime(sales_end_str, '%m/%d/%Y %H:%M')
                ticket.hide = hide
                ticket.description = ticket_descriptions[i]
                ticket.description_toggle = description_toggle
                ticket.quantity = ticket_quantities[i]
                ticket.min_order = ticket_min_orders[i]
                ticket.max_order = ticket_max_orders[i]
                ticket.tags = tag_list

                save_to_db(ticket)

        # Remove all the tickets that are not in form
        # except those that already have placed orders
        for ticket in event.tickets:
            if ticket.name not in ticket_names and not ticket.has_order_tickets():
                delete_from_db(ticket, 'Delete ticket')

        event.ticket_url = form.get('ticket_url', None)

        if not event.ticket_url:

            event.ticket_url = url_for('event_detail.display_event_tickets',
                                       identifier=event.identifier,
                                       _external=True)
            if form['taxAllow'] == 'taxNo':
                event.tax_allow = False
                delete_from_db(tax, "Tax options deleted")

            if form['taxAllow'] == 'taxYes':
                event.tax_allow = True

                tax_invoice = False
                if 'tax_invoice' in form:
                    tax_invoice = True

                tax_include_in_price = False
                if form['tax_options'] == 'tax_include':
                    tax_include_in_price = True

                if not tax:
                    tax = Tax(country=form['tax_country'],
                              tax_name=form['tax_name'],
                              tax_rate=form['tax_rate'],
                              tax_id=form['tax_id'],
                              send_invoice=tax_invoice,
                              registered_company=form.get('registered_company', ''),
                              address=form.get('buisness_address', ''),
                              city=form.get('invoice_city', ''),
                              state=form.get('invoice_state', ''),
                              zip=form.get('invoice_zip', 0),
                              invoice_footer=form.get('invoice_footer', ''),
                              tax_include_in_price=tax_include_in_price,
                              event_id=event.id)

                    save_to_db(tax, "Tax ")

                if tax:
                    tax.country = form['tax_country'],
                    tax.tax_name = form['tax_name'],
                    tax.tax_rate = form['tax_rate'],
                    tax.tax_id = form['tax_id'],
                    tax.send_invoice = tax_invoice,
                    tax.registered_company = form.get('registered_company', ''),
                    tax.address = form.get('buisness_address', ''),
                    tax.city = form.get('invoice_city', ''),
                    tax.state = form.get('invoice_state', ''),
                    tax.zip = form.get('invoice_zip', 0),
                    tax.invoice_footer = form.get('invoice_footer', ''),
                    tax.tax_include_in_price = tax_include_in_price,
                    tax.event_id = event.id

                    save_to_db(tax, "Tax Options Updated")

        event = DataManager.update_searchable_location_name(event)

        if form.get('organizer_state', u'off') == u'on':
            event.organizer_name = form['organizer_name']
            event.organizer_description = form['organizer_description']
        else:
            event.organizer_name = ""
            event.organizer_description = ""

        if form.get('coc_state', u'off') == u'on':
            event.code_of_conduct = form['code_of_conduct']
        else:
            event.code_of_conduct = ""

        if not event.copyright:
            # It is possible that the copyright is set as None before.
            # Set it as an `EventCopyright` object.
            event.copyright = EventCopyright()
        # Filter out Copyright info
        event.copyright.holder = form.get('organizer_name')
        licence_name = form.get('copyright_licence')
        # Ignoring Licence description
        _, _, licence_url, logo, _ = EVENT_LICENCES.get(licence_name, ('',) * 5)

        event.copyright.licence = licence_name
        event.copyright.licence_url = licence_url
        event.copyright.logo = logo

        state = form.get('state', None)
        if state and ((state == u'Published' and not string_empty(
            event.location_name)) or state != u'Published') and login.current_user.is_verified:
            event.state = state

        social_link_name = form.getlist('social[name]')
        social_link_link = form.getlist('social[link]')
        social_link_id = form.getlist('social[id]')

        sponsor_name = form.getlist('sponsors[name]')
        sponsor_logo_url = []
        sponsor_url = form.getlist('sponsors[url]')
        sponsor_type = form.getlist('sponsors[type]')
        sponsor_level = form.getlist('sponsors[level]')
        sponsor_description = form.getlist('sponsors[description]')

        custom_forms_name = form.getlist('custom_form[name]')
        custom_forms_value = form.getlist('custom_form[value]')

        for social_link in social_links:
            if str(social_link.id) not in social_link_id:
                delete_from_db(social_link, "SocialLink Deleted")

        for index, name in enumerate(social_link_name):
            if not string_empty(social_link_link[index]):
                # If 'Website' has been provided,
                # save it as Holder URL for Copyright
                if name.lower() == 'website':
                    event.copyright.holder_url = social_link_link[index]

                if social_link_id[index] != '':
                    social_link, c = get_or_create(SocialLink,
                                                   id=social_link_id[index],
                                                   event_id=event.id)
                    social_link.name = name
                    social_link.link = social_link_link[index]
                else:
                    social_link, c = get_or_create(SocialLink,
                                                   name=name,
                                                   link=social_link_link[index],
                                                   event_id=event.id)
                db.session.add(social_link)

        if event.stripe:
            delete_from_db(event.stripe, "Old stripe auth deleted")

        if 'pay_by_stripe' in form:
            if form.get('stripe_added', u'no') == u'yes':
                stripe_authorization = StripeAuthorization(
                    stripe_secret_key=form.get('stripe_secret_key', ''),
                    stripe_refresh_token=form.get('stripe_refresh_token', ''),
                    stripe_publishable_key=form.get('stripe_publishable_key', ''),
                    stripe_user_id=form.get('stripe_user_id', ''),
                    stripe_email=form.get('stripe_email', ''),
                    event_id=event.id
                )
                save_to_db(stripe_authorization)

        if form.get('has_session_speakers', u'no') == u'yes':

            session_type_names = form.getlist('session_type[name]')
            session_type_id = form.getlist('session_type[id]')
            session_type_length = form.getlist('session_type[length]')

            track_name = form.getlist('tracks[name]')
            track_color = form.getlist('tracks[color]')
            track_id = form.getlist('tracks[id]')

            room_name = form.getlist('rooms[name]')
            room_floor = form.getlist('rooms[floor]')
            room_id = form.getlist('rooms[id]')

            event.has_session_speakers = True
            # save the edited info to database
            for session_type in session_types:
                if str(session_type.id) not in session_type_id:
                    delete_from_db(session_type, "SessionType Deleted")

            for index, name in enumerate(session_type_names):
                if not string_empty(name):
                    if session_type_id[index] != '':
                        session_type, c = get_or_create(SessionType,
                                                        id=session_type_id[index],
                                                        event_id=event.id)
                        session_type.name = name
                        session_type.length = session_type_length[index]
                    else:
                        session_type, c = get_or_create(SessionType,
                                                        name=name,
                                                        length=session_type_length[index],
                                                        event_id=event.id)
                    db.session.add(session_type)

            for track in tracks:
                if str(track.id) not in track_id:
                    delete_from_db(track, "Track Deleted")

            for index, name in enumerate(track_name):
                if not string_empty(name):
                    if track_id[index] != '':
                        track, c = get_or_create(Track,
                                                 id=track_id[index],
                                                 event_id=event.id)
                        track.name = name
                        track.color = track_color[index].upper()
                    else:
                        track, c = get_or_create(Track,
                                                 name=name,
                                                 color=track_color[index].upper(),
                                                 event_id=event.id)
                    db.session.add(track)

            for room in microlocations:
                if str(room.id) not in room_id:
                    delete_from_db(room, "Room Deleted")

            for index, name in enumerate(room_name):
                if not string_empty(name):
                    if room_id[index] != '':
                        room, c = get_or_create(Microlocation,
                                                id=room_id[index],
                                                event_id=event.id)
                        room.name = name
                        room.floor = room_floor[index] if room_floor[index] != '' else None
                    else:
                        room, c = get_or_create(Microlocation,
                                                name=name,
                                                floor=room_floor[index] if room_floor[index] != '' else None,
                                                event_id=event.id)
                    db.session.add(room)

            if call_for_papers:
                call_for_papers.announcement = form['announcement']
                call_for_papers.hash = form['cfs_hash']
                call_for_papers.start_date = datetime.strptime(
                    form['cfs_start_date'], '%m/%d/%Y')
                call_for_papers.end_date = datetime.strptime(
                    form['cfs_end_date'], '%m/%d/%Y')
                call_for_papers.privacy = form['cfs_privacy']
                call_for_papers.event_id = event.id
                save_to_db(call_for_papers)
            else:
                call_for_speakers, c = get_or_create(CallForPaper,
                                                     announcement=form['announcement'],
                                                     start_date=datetime.strptime(
                                                         form['cfs_start_date'] + ' ' + form['cfs_start_time'],
                                                         '%m/%d/%Y %H:%M'),
                                                     end_date=datetime.strptime(
                                                         form['cfs_end_date'] + ' ' + form['cfs_end_time'],
                                                         '%m/%d/%Y %H:%M'),
                                                     hash=form['cfs_hash'],
                                                     privacy=form['cfs_privacy'],
                                                     timezone=form.get('cfs_timezone', 'UTC'),
                                                     event_id=event.id)
                save_to_db(call_for_speakers)
        else:
            event.has_session_speakers = False
            for session in DataGetter.get_sessions_by_event_id(event.id):
                delete_from_db(session, "Removed session")
            for speaker in DataGetter.get_speakers(event.id):
                delete_from_db(speaker, "Removed speaker")
            if call_for_papers:
                delete_from_db(call_for_papers, "Removed cfs")
            for session_type in session_types:
                delete_from_db(session_type, "session type removed")
            for track in tracks:
                delete_from_db(track, "track removed")
            for microlocation in microlocations:
                delete_from_db(microlocation, "microlocation removed")

        for sponsor in sponsors:
            delete_from_db(sponsor, "Sponsor Deleted")

        if form.get('sponsors_state', u'off') == u'on':
            for index, name in enumerate(sponsor_name):
                if not string_empty(name):
                    sponsor = Sponsor(name=name, url=sponsor_url[index],
                                      level=sponsor_level[index], description=sponsor_description[index],
                                      event_id=event.id, sponsor_type=sponsor_type[index])
                    save_to_db(sponsor, "Sponsor created")
                    if len(img_files) != 0:
                        if img_files[index]:
                            img_url = upload(
                                img_files[index],
                                UPLOAD_PATHS['sponsors']['logo'].format(
                                    event_id=int(event.id), id=int(sponsor.id)
                                ))
                            sponsor_logo_url.append(img_url)
                            sponsor.logo = sponsor_logo_url[index]
                        else:
                            if name in old_sponsor_names:
                                sponsor.logo = old_sponsor_logos[index]
                            else:
                                sponsor.logo = ""
                    else:
                        if name in old_sponsor_names:
                            sponsor.logo = old_sponsor_logos[index]
                        else:
                            sponsor.logo = ""
                    print sponsor.logo
                    save_to_db(sponsor, "Sponsor updated")

        session_form = ""
        speaker_form = ""
        for index, name in enumerate(custom_forms_name):
            if name == "session_form":
                session_form = custom_forms_value[index]
            elif name == "speaker_form":
                speaker_form = custom_forms_value[index]

        update_or_create(
            CustomForms, event_id=event.id,
            session_form=session_form, speaker_form=speaker_form)

        for _ in get_all_columns():  # update all columns; safe way
            update_version(event.id, False, _)

        save_to_db(event, "Event saved")
        record_activity('update_event', event_id=event.id)
        return event

    @staticmethod
    def delete_event(e_id):
        EventsUsers.query.filter_by(event_id=e_id).delete()
        UsersEventsRoles.query.filter_by(event_id=e_id).delete()
        EmailNotification.query.filter_by(event_id=e_id).delete()
        SessionType.query.filter_by(event_id=e_id).delete()
        SocialLink.query.filter_by(event_id=e_id).delete()
        Track.query.filter_by(id=e_id).delete()
        Invite.query.filter_by(event_id=e_id).delete()
        Session.query.filter_by(event_id=e_id).delete()
        Event.query.filter_by(id=e_id).delete()
        # record_activity('delete_event', event_id=e_id)
        db.session.commit()

    @staticmethod
    def trash_event(e_id):
        event = Event.query.get(e_id)
        event.in_trash = True
        event.trash_date = datetime.now()
        save_to_db(event, "Event Added to Trash")
        return event

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
        file_obj = File.query.get(file_id)
        os.remove(os.path.join(os.path.realpath('.') + '/static/', file_obj.name))
        delete_from_db(file_obj, "File removed")
        flash("File removed")

    @staticmethod
    def add_role_to_event(form, event_id, record=True):
        user = User.query.filter_by(email=form['user_email']).first()
        role = Role.query.filter_by(name=form['user_role']).first()
        uer = UsersEventsRoles(event=Event.query.get(event_id),
                               user=user, role=role)
        save_to_db(uer, "UserEventRole saved")
        if record:
            record_activity('create_role', role=role, user=user, event_id=event_id)

    @staticmethod
    def add_attendee_role_to_event(user, event_id):
        role = Role.query.filter_by(name=ATTENDEE).first()
        uer = UsersEventsRoles(event=Event.query.get(event_id), user=user, role=role)
        save_to_db(uer, "Attendee saved")

    @staticmethod
    def decline_role_invite(role_invite):
        role_invite.declined = True
        save_to_db(role_invite)

    @staticmethod
    def update_user_event_role(form, uer):
        role = Role.query.filter_by(name=form['user_role']).first()
        user = User.query.filter_by(email=form['user_email']).first()
        uer.user = user
        uer.role_id = role.id
        save_to_db(uer, "Event saved")
        record_activity('update_role', role=role, user=user, event_id=uer.event_id)

    @staticmethod
    def create_page(form):

        page = Page(name=form.get('name', ''), title=form.get('title', ''), description=form.get('description', ''),
                    url=form.get('url', ''), place=form.get('place', ''), index=form.get('index', 0))
        save_to_db(page, "Page created")
        cache.delete('pages')

    def update_page(self, page, form):
        page.name = form.get('name', '')
        page.title = form.get('title', '')
        page.description = form.get('description', '')
        page.url = form.get('url', '')
        page.place = form.get('place', '')
        page.index = form.get('index', '')
        save_to_db(page, "Page updated")
        cache.delete('pages')

    @staticmethod
    def create_or_update_message_settings(form):

        for mail in MAILS:
            mail_status = 1 if form.get(mail + '_mail_status', 'off') == 'on' else 0
            notif_status = 1 if form.get(mail + '_notif_status', 'off') == 'on' else 0
            user_control_status = 1 if form.get(mail + '_user_control_status', 'off') == 'on' else 0
            message_setting = MessageSettings.query.filter_by(action=mail).first()
            if message_setting:
                message_setting.mail_status = mail_status
                message_setting.notif_status = notif_status
                message_setting.user_control_status = user_control_status
                save_to_db(message_setting, "Message Settings Updated")
            else:
                message_setting = MessageSettings(action=mail,
                                                  mail_status=mail_status,
                                                  notif_status=notif_status,
                                                  user_control_status=user_control_status)
                save_to_db(message_setting, "Message Settings Updated")


def save_to_db(item, msg="Saved to db", print_error=True):
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
        if print_error:
            print e
            traceback.print_exc()
        logging.error('DB Exception! %s' % e)
        db.session.rollback()
        return False


def delete_from_db(item, msg='Deleted from db'):
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
    except Exception, error:
        logging.error('DB Exception! %s' % error)
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


def get_instagram_auth(state=None, token=None):
    if token:
        return OAuth2Session(InstagramOAuth.get_client_id(), token=token)
    if state:
        return OAuth2Session(InstagramOAuth.get_client_id(), state=state,
                             redirect_uri=InstagramOAuth.get_redirect_uri())
    # scope = "+".join(InstagramOAuth.SCOPE)
    oauth = OAuth2Session(InstagramOAuth.get_client_id(), redirect_uri=InstagramOAuth.get_redirect_uri())
    return oauth


def get_twitter_auth_url():
    consumer = oauth2.Consumer(key=TwitterOAuth.get_client_id(),
                               secret=TwitterOAuth.get_client_secret())
    client = oauth2.Client(consumer)
    resp, content = client.request('https://api.twitter.com/oauth/request_token', "GET")
    return content + "&redirect_uri" + TwitterOAuth.get_redirect_uri(), consumer



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
    user_detail = UserDetail.query.filter_by(user_id=user.id).first()
    user_detail.avatar_uploaded = user.avatar
    user_detail.firstname = user_data['name']
    save_to_db(user, "User Details Updated")
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
    sequence = '"%s"'
    # add more information for objects
    for k in kwargs:
        v = kwargs[k]
        if k.find('_id') > -1:
            kwargs[k] = str(v)
        elif k.startswith('user'):
            kwargs[k] = sequence % v.email + id_str % v.id
        elif k.startswith('role'):
            kwargs[k] = sequence % v.title_name
        elif k.startswith('session'):
            kwargs[k] = sequence % v.title + id_str % v.id
        elif k.startswith('track'):
            kwargs[k] = sequence % v.name + id_str % v.id
        elif k.startswith('speaker'):
            kwargs[k] = sequence % v.name + id_str % v.id
        else:
            kwargs[k] = str(v)
    try:
        msg = ACTIVITIES[template].format(**kwargs)
    except Exception:  # in case some error happened, not good
        msg = '[ERROR LOGGING] %s' % template
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


def update_or_create(model, event_id, **kwargs):
    """
    Update or create an item based on event id as PK
    """
    was_created = False
    instance = db.session.query(model).filter_by(event_id=event_id).first()
    if instance:
        db.session.query(model).filter_by(event_id=event_id).update(kwargs)
    else:
        was_created = True
        instance = model(event_id=event_id, **kwargs)
    db.session.add(instance)
    db.session.commit()
    return instance, was_created


def update_role_to_admin(form, user_id):
    user = DataGetter.get_user(user_id)
    old_admin_status = user.is_admin
    if form['admin_perm'] == 'isAdmin':
        user.is_admin = True
    else:
        user.is_admin = False

    save_to_db(user, "User role Updated")
    if old_admin_status != user.is_admin:
        record_activity(
            'system_admin', user=user,
            status='Assigned' if user.is_admin else 'Unassigned'
        )


def trash_user(user_id):
    user = DataGetter.get_user(user_id)
    user.in_trash = True
    user.trash_date = datetime.now()
    save_to_db(user, 'User has been added to trash')
    return user


def trash_session(session_id):
    session = DataGetter.get_session(session_id)
    session.in_trash = True
    session.trash_date = datetime.now()
    save_to_db(session, "Session added to Trash")
    update_version(session.event_id, False, 'sessions_ver')
    return session


def restore_event(event_id):
    event = DataGetter.get_event(event_id)
    event.in_trash = False
    save_to_db(event, "Event restored from Trash")


def restore_user(user_id):
    user = DataGetter.get_user(user_id)
    user.in_trash = False
    save_to_db(user, "User restored from Trash")


def restore_session(session_id):
    session = DataGetter.get_session(session_id)
    session.in_trash = False
    save_to_db(session, "Session restored from Trash")
    update_version(session.event_id, False, 'sessions_ver')


def create_modules(form):
    modules_form_value = form.getlist('modules_form[value]')
    module = DataGetter.get_module()

    if module is None:
        module = Module()

    if str(modules_form_value[0][24]) == '1':
        module.ticket_include = True
    else:
        module.ticket_include = False

    if str(modules_form_value[0][49]) == '1':
        module.payment_include = True
    else:
        module.payment_include = False

    if str(modules_form_value[0][75]) == '1':
        module.donation_include = True
    else:
        module.donation_include = False

    save_to_db(module, "Module settings saved")
    events = DataGetter.get_all_events()

    if module.ticket_include:
        for event in events:
            event.ticket_include = True
            save_to_db(event, "Event updated")
