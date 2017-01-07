import json
import logging
import os.path
import random
import shutil
import time
import traceback
from datetime import datetime, timedelta
from os import path
from urllib2 import urlopen

import PIL
import oauth2
from PIL import Image
from flask import flash, url_for, g, current_app
from flask.ext import login
from flask.ext.scrypt import generate_password_hash, generate_random_salt
from flask_socketio import emit
from requests_oauthlib import OAuth2Session
from sqlalchemy.orm import make_transient

from app.helpers.cache import cache
from app.helpers.helpers import string_empty, string_not_empty
from app.helpers.notification_email_triggers import trigger_new_session_notifications, \
    trigger_session_state_change_notifications
from app.helpers.oauth import OAuth, FbOAuth, InstagramOAuth, TwitterOAuth
from app.helpers.storage import upload, UPLOAD_PATHS, UploadedFile, upload_local
from app.models.notifications import Notification
from app.helpers import helpers as Helper
from app.helpers.data_getter import DataGetter
from app.helpers.system_mails import MAILS
from app.helpers.update_version import VersionUpdater
from app.models import db
from app.models.activity import Activity, ACTIVITIES
from app.models.call_for_papers import CallForPaper
from app.models.email_notifications import EmailNotification
from app.models.event import Event, EventsUsers
from app.models.image_sizes import ImageSizes
from app.models.invite import Invite
from app.models.message_settings import MessageSettings
from app.models.microlocation import Microlocation
from app.models.page import Page
from app.models.panel_permissions import PanelPermission
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_invite import RoleInvite
from app.models.service import Service
from app.models.session import Session
from app.models.session_type import SessionType
from app.models.social_link import SocialLink
from app.models.speaker import Speaker
from app.models.sponsor import Sponsor
from app.models.system_role import CustomSysRole, UserSystemRole
from app.models.track import Track
from app.models.user import User, ATTENDEE
from app.models.user_detail import UserDetail
from app.models.user_permissions import UserPermission
from app.models.users_events_roles import UsersEventsRoles


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
              'notifs': user.get_unread_notifs()},
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
        role_invite = RoleInvite(email=email.lower(),
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
                              level=form.get('level', ''),
                              comments=form.get('comments',''),
                              language=form.get('language',''),
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
                              city=form.get('city', ''),
                              heard_from = form.get('other_text', None) if form.get('heard_from', None) == "Other" else form.get('heard_from', None),
                              sponsorship_required=form.get('sponsorship_required', ''),
                              speaking_experience=form.get('speaking_experience', ''),
                              long_biography=form.get('long_biography',''),
                              mobile=form.get('mobile',''),
                              user=login.current_user if login and login.current_user.is_authenticated else None)

        new_session.speakers.append(speaker)

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
        logo = form.get('photo', None)
        if string_not_empty(logo) and logo:
            filename = '{}.png'.format(time.time())
            filepath = '{}/static/{}'.format(path.realpath('.'),
                                             logo[len('/serve_static/'):])
            try:
                logo_file = UploadedFile(filepath, filename)
                logo = upload(logo_file, 'events/%d/speakers/%d/photo' % (int(event_id), int(speaker.id)))
                speaker.photo = logo
                image_sizes = DataGetter.get_image_sizes_by_type(type='profile')
                if not image_sizes:
                    image_sizes = ImageSizes(full_width=150,
                                             full_height=150,
                                             icon_width=35,
                                             icon_height=35,
                                             thumbnail_width=50,
                                             thumbnail_height=50,
                                             type='profile')
                save_to_db(image_sizes, "Image Sizes Saved")
                filename = '{}.jpg'.format(time.time())
                filepath = '{}/static/{}'.format(path.realpath('.'),
                                                 logo[len('/serve_static/'):])
                logo_file = UploadedFile(filepath, filename)

                temp_img_file = upload_local(logo_file,
                                             'events/{event_id}/speakers/{id}/temp'.format(
                                                 event_id=int(event_id), id=int(speaker.id)))
                temp_img_file = temp_img_file.replace('/serve_', '')

                basewidth = image_sizes.full_width
                img = Image.open(temp_img_file)
                hsize = image_sizes.full_height
                img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
                img.save(temp_img_file)
                file_name = temp_img_file.rsplit('/', 1)[1]
                large_file = UploadedFile(file_path=temp_img_file, filename=file_name)
                profile_thumbnail_url = upload(
                    large_file,
                    UPLOAD_PATHS['speakers']['thumbnail'].format(
                        event_id=int(event_id), id=int(speaker.id)
                    ))

                basewidth = image_sizes.thumbnail_width
                img = Image.open(temp_img_file)
                hsize = image_sizes.thumbnail_height
                img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
                img.save(temp_img_file)
                file_name = temp_img_file.rsplit('/', 1)[1]
                thumbnail_file = UploadedFile(file_path=temp_img_file, filename=file_name)
                profile_small_url = upload(
                    thumbnail_file,
                    UPLOAD_PATHS['speakers']['small'].format(
                        event_id=int(event_id), id=int(speaker.id)
                    ))

                basewidth = image_sizes.icon_width
                img = Image.open(temp_img_file)
                hsize = image_sizes.icon_height
                img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
                img.save(temp_img_file)
                file_name = temp_img_file.rsplit('/', 1)[1]
                icon_file = UploadedFile(file_path=temp_img_file, filename=file_name)
                profile_icon_url = upload(
                    icon_file,
                    UPLOAD_PATHS['speakers']['icon'].format(
                        event_id=int(event_id), id=int(speaker.id)
                    ))
                shutil.rmtree(path='static/media/' + 'events/{event_id}/speakers/{id}/temp'.format(
                    event_id=int(event_id), id=int(speaker.id)))
                speaker.thumbnail = profile_thumbnail_url
                speaker.small = profile_small_url
                speaker.icon = profile_icon_url
                save_to_db(speaker, "Speaker photo saved")
                record_activity('update_speaker', speaker=speaker, event_id=event_id)
            except:
                pass
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
                              city=form.get('city', ''),
                              heard_from = form.get('other_text', None) if form.get('heard_from', None) == "Other" else form.get('heard_from', None),
                              sponsorship_required=form.get('sponsorship_required', ''),
                              speaking_experience=form.get('speaking_experience', ''),
                              user=user if login and login.current_user.is_authenticated else None)
            save_to_db(speaker, "Speaker saved")
            record_activity('create_speaker', speaker=speaker, event_id=event_id)
        if speaker_img_file != "":
            speaker_img = upload(
                speaker_img_file,
                UPLOAD_PATHS['speakers']['photo'].format(
                    event_id=int(event_id), id=int(speaker.id)
                ))
            speaker.photo = speaker_img
            save_to_db(speaker, "Speaker photo saved")
            record_activity('update_speaker', speaker=speaker, event_id=event_id)
        logo = form.get('photo', None)

        if string_not_empty(logo) and logo:
            filename = '{}.png'.format(time.time())
            filepath = '{}/static/{}'.format(path.realpath('.'),
                                             logo[len('/serve_static/'):])
            logo_file = UploadedFile(filepath, filename)
            logo = upload(logo_file, 'events/%d/speakers/%d/photo' % (int(event_id), int(speaker.id)))
            speaker.photo = logo
            image_sizes = DataGetter.get_image_sizes_by_type(type='profile')
            if not image_sizes:
                image_sizes = ImageSizes(full_width=150,
                                         full_height=150,
                                         icon_width=35,
                                         icon_height=35,
                                         thumbnail_width=50,
                                         thumbnail_height=50,
                                         type='profile')
            save_to_db(image_sizes, "Image Sizes Saved")
            filename = '{}.jpg'.format(time.time())
            filepath = '{}/static/{}'.format(path.realpath('.'),
                                             logo[len('/serve_static/'):])
            logo_file = UploadedFile(filepath, filename)

            temp_img_file = upload_local(logo_file,
                                         'events/{event_id}/speakers/{id}/temp'.format(
                                             event_id=int(event_id), id=int(speaker.id)))
            temp_img_file = temp_img_file.replace('/serve_', '')

            basewidth = image_sizes.full_width
            img = Image.open(temp_img_file)
            hsize = image_sizes.full_height
            img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
            img.save(temp_img_file)
            file_name = temp_img_file.rsplit('/', 1)[1]
            large_file = UploadedFile(file_path=temp_img_file, filename=file_name)
            profile_thumbnail_url = upload(
                large_file,
                UPLOAD_PATHS['speakers']['thumbnail'].format(
                    event_id=int(event_id), id=int(speaker.id)
                ))

            basewidth = image_sizes.thumbnail_width
            img = Image.open(temp_img_file)
            hsize = image_sizes.thumbnail_height
            img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
            img.save(temp_img_file)
            file_name = temp_img_file.rsplit('/', 1)[1]
            thumbnail_file = UploadedFile(file_path=temp_img_file, filename=file_name)
            profile_small_url = upload(
                thumbnail_file,
                UPLOAD_PATHS['speakers']['small'].format(
                    event_id=int(event_id), id=int(speaker.id)
                ))

            basewidth = image_sizes.icon_width
            img = Image.open(temp_img_file)
            hsize = image_sizes.icon_height
            img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
            img.save(temp_img_file)
            file_name = temp_img_file.rsplit('/', 1)[1]
            icon_file = UploadedFile(file_path=temp_img_file, filename=file_name)
            profile_icon_url = upload(
                icon_file,
                UPLOAD_PATHS['speakers']['icon'].format(
                    event_id=int(event_id), id=int(speaker.id)
                ))
            shutil.rmtree(path='static/media/' + 'events/{event_id}/speakers/{id}/temp'.format(
                event_id=int(event_id), id=int(speaker.id)))
            speaker.thumbnail = profile_thumbnail_url
            speaker.small = profile_small_url
            speaker.icon = profile_icon_url
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
    def session_accept_reject(session, event_id, state, send_email=True):
        session.state = state
        session.submission_date = datetime.now()
        session.submission_modifier = login.current_user.email
        session.state_email_sent = False
        save_to_db(session, 'Session State Updated')
        if send_email:
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

            if form_state == 'pending' and session.state != 'pending' and \
                    session.state != 'accepted' and session.state != 'rejected':

                trigger_new_session_notifications(session.id, event_id=event_id)

            session.title = form.get('title', '')
            session.subtitle = form.get('subtitle', '')
            session.long_abstract = form.get('long_abstract', '')
            session.short_abstract = form.get('short_abstract', '')
            session.level = form.get('level', '')
            session.state = form_state
            session.track_id = form.get('track', None) if form.get('track', None) != "" else  None
            session.session_type_id = form.get('session_type', None) if form.get('session_type', None) != "" else None

            existing_speaker_ids = form.getlist("speakers[]")
            current_speaker_ids = []
            existing_speaker_ids_by_email = []

            save_to_db(session, 'Session Updated')

            for existing_speaker in DataGetter.get_speaker_by_email(form.get("email")).all():
                existing_speaker_ids_by_email.append(str(existing_speaker.id))

            for current_speaker in session.speakers:
                current_speaker_ids.append(str(current_speaker.id))

            for current_speaker_id in current_speaker_ids:
                if current_speaker_id not in existing_speaker_ids and current_speaker_id \
                     not in existing_speaker_ids_by_email:

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
    def update_user(form, user_id, contacts_only_update=False):

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
            Helper.send_notif_when_changes_email(user, user.email, form['email'])
            Helper.send_email_confirmation(form, link)
            user.email = form['email']

        user_detail.contact = form['contact']
        if not contacts_only_update:
            user_detail.firstname = form['firstname']
            user_detail.lastname = form['lastname']

            if form['facebook'].strip() != '':
                user_detail.facebook = 'https://facebook.com/' + form['facebook'].strip()
            else:
                user_detail.facebook = ''

            if form['twitter'].strip() != '':
                user_detail.twitter = 'https://twitter.com/' + form['twitter'].strip()
            else:
                user_detail.twitter = ''

            if form['instagram'].strip() != '':
                user_detail.instagram = 'https://instagram.com/' + form['instagram'].strip()
            else:
                user_detail.instagram = ''

            if form['google'].strip() != '':
                user_detail.google = 'https://plus.google.com/' + form['google'].strip()
            else:
                user_detail.google = ''

            user_detail.details = form['details']
            avatar_img = form.get('avatar-img', None)
            user_detail.avatar_uploaded = ""
            user_detail.thumbnail = ""
            user_detail.small = ""
            user_detail.icon = ""
            if string_not_empty(avatar_img) and avatar_img:
                filename = '{}.png'.format(time.time())
                filepath = '{}/static/{}'.format(path.realpath('.'),
                                                 avatar_img[len('/serve_static/'):])
                # print "File path 1", filepath
                avatar_img_file = UploadedFile(filepath, filename)
                avatar_img_temp = upload(avatar_img_file, 'users/%d/avatar' % int(user_id))
                user_detail.avatar_uploaded = avatar_img_temp
                image_sizes = DataGetter.get_image_sizes_by_type(type='profile')
                if not image_sizes:
                    image_sizes = ImageSizes(full_width=150,
                                             full_height=150,
                                             icon_width=35,
                                             icon_height=35,
                                             thumbnail_width=50,
                                             thumbnail_height=50,
                                             type='profile')
                save_to_db(image_sizes, "Image Sizes Saved")
                filename = '{}.jpg'.format(time.time())
                filepath = '{}/static/{}'.format(path.realpath('.'),
                                                 avatar_img[len('/serve_static/'):])
                # print "File path 1", filepath
                avatar_img_file = UploadedFile(filepath, filename)

                temp_img_file = upload_local(avatar_img_file,
                                             'users/{user_id}/temp'.format(user_id=int(user_id)))
                temp_img_file = temp_img_file.replace('/serve_', '')

                basewidth = image_sizes.full_width
                img = Image.open(temp_img_file)
                hsize = image_sizes.full_height
                img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
                img.save(temp_img_file)
                file_name = temp_img_file.rsplit('/', 1)[1]
                large_file = UploadedFile(file_path=temp_img_file, filename=file_name)
                profile_thumbnail_url = upload(
                    large_file,
                    UPLOAD_PATHS['user']['thumbnail'].format(
                        user_id=int(user_id)
                    ))

                basewidth = image_sizes.thumbnail_width
                img = Image.open(temp_img_file)
                hsize = image_sizes.thumbnail_height
                img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
                img.save(temp_img_file)
                file_name = temp_img_file.rsplit('/', 1)[1]
                thumbnail_file = UploadedFile(file_path=temp_img_file, filename=file_name)
                profile_small_url = upload(
                    thumbnail_file,
                    UPLOAD_PATHS['user']['small'].format(
                        user_id=int(user_id)
                    ))

                basewidth = image_sizes.icon_width
                img = Image.open(temp_img_file)
                hsize = image_sizes.icon_height
                img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
                img.save(temp_img_file)
                file_name = temp_img_file.rsplit('/', 1)[1]
                icon_file = UploadedFile(file_path=temp_img_file, filename=file_name)
                profile_icon_url = upload(
                    icon_file,
                    UPLOAD_PATHS['user']['icon'].format(
                        user_id=int(user_id)
                    ))
                shutil.rmtree(path='static/media/' + 'users/{user_id}/temp'.format(user_id=int(user_id)))
                user_detail.thumbnail = profile_thumbnail_url
                user_detail.small = profile_small_url
                user_detail.icon = profile_icon_url
        user, user_detail, save_to_db(user, "User updated")
        record_activity('update_user', user=user)

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
    def create_custom_sys_role(form):
        role_name = form.get('role_name')
        sys_role = CustomSysRole(name=role_name)
        save_to_db(sys_role)
        from app.views.super_admin import PANEL_LIST
        for panel in PANEL_LIST:
            if form.get(panel):
                perm = PanelPermission(panel, sys_role, True)
            else:
                perm = PanelPermission(panel, sys_role, False)
            save_to_db(perm)

    @staticmethod
    def update_custom_sys_role(form):
        role_name = form.get('role_name')
        sys_role = CustomSysRole.query.filter_by(name=role_name).first()
        sys_role.name = form.get('new_role_name')
        db.session.add(sys_role)
        from app.views.super_admin import PANEL_LIST
        for panel in PANEL_LIST:
            perm, _ = get_or_create(PanelPermission, panel_name=panel,
                                    role=sys_role)
            if form.get(panel):
                perm.can_access = True
            else:
                perm.can_access = False
            db.session.add(perm)

        db.session.commit()

    @staticmethod
    def delete_custom_sys_role(role_id):
        sys_role = CustomSysRole.query.get(role_id)
        if sys_role:
            delete_from_db(sys_role, 'System Role deleted')

    @staticmethod
    def get_or_create_user_sys_role(user, role):
        role, _ = get_or_create(UserSystemRole, user=user, role=role)
        save_to_db(role, 'Custom System Role saved')

    @staticmethod
    def delete_user_sys_role(user, role):
        role = UserSystemRole.query.filter_by(user=user, role=role).first()
        if role:
            delete_from_db(role, 'Custom System Role deleted')

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
                    url=form.get('url', ''), place=form.get('place', ''), index=form.get('index', 0),
                    language=form.get('language', 'en'))
        save_to_db(page, "Page created")
        cache.delete('pages')

    @staticmethod
    def update_page(page, form):
        page.name = form.get('name', '')
        page.title = form.get('title', '')
        page.description = form.get('description', '')
        page.url = form.get('url', '')
        page.place = form.get('place', '')
        page.index = form.get('index', '')
        page.language = form.get('language', 'en')
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
    :param print_error:
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
    if 'http' in user.avatar:
        f_name, uploaded_file = uploaded_file_provided_by_url(user.avatar)
        avatar = upload(uploaded_file, 'users/%d/avatar' % int(user.id))
        user_detail.avatar_uploaded = avatar

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
    """Function responsible for increasing version when some data will be
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
    user.is_admin = True if form['admin_perm'] == 'isAdmin' else False

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


def uploaded_file_provided_by_url(url):
    response_file = urlopen(url)
    filename = str(time.time()) + '.jpg'
    file_path = os.path.realpath('.') + '/static/uploads/' + filename
    fh = open(file_path, "wb")
    fh.write(response_file.read())
    fh.close()
    return filename, UploadedFile(file_path, filename)
