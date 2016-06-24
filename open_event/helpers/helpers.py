"""Copyright 2015 Rafal Kowalski"""
import json
import os
import re
import requests
from datetime import datetime
from flask import request
from itsdangerous import Serializer
from flask.ext import login
from ..models.track import Track
from ..models.mail import INVITE_PAPERS, NEW_SESSION, USER_CONFIRM, \
    USER_REGISTER, PASSWORD_RESET, Mail


def get_event_id():
    """Get event Id from request url"""
    url = request.url
    result = re.search('event\/[0-9]*', url)
    return result.group(0).split('/')[1]


def is_track_name_unique_in_event(form, event_id, *args):
    """Check unique of track name in event"""
    track_name = form.name.data
    track_id = args[0] if len(args) else None
    tracks = Track.query.filter_by(event_id=event_id, name=track_name)
    if not track_id:
        return tracks.count() == 0
    else:
        for track in tracks.all():
            return str(track.id) == track_id
        return True

HEADERS = {
    "Authorization": ("Bearer SG.55ztiWJxQYuYK7ToThxDPA.rAc929FzcDQsyj"
                      "VwmIvKlPoc1YVpKCSOwhEFWZvxFT8")
}


def send_email_invitation(email, event_name, link):
    """Send email for submit papers"""
    send_email(
        to=email,
        action=INVITE_PAPERS,
        subject='Invitation to Submit Papers for ' + event_name,
        html=("Hi %s<br/>" % str(email) +
              "You are invited to submit papers for event: %s" % str(event_name) +
              "<br/> Visit this link to fill up details: %s" % link)
    )


def send_new_session_organizer(email, event_name, link):
    """Send email after new sesions proposal"""
    send_email(
        to=email,
        action=NEW_SESSION,
        subject="New session proposal for " + event_name,
        html=("Hi %s<br/>" % str(email) +
              "The event <strong>%s</strong> has received a new session proposal. " % str(event_name) +
              "<br/> Visit this link to view the session: %s" % link)
    )


def send_email_after_account_create(form):
    """Send email after account create"""
    send_email(
        to=form['email'],
        action=USER_REGISTER,
        subject="Account Created on Open Event",
        html=("Your Account Has Been Created! Congratulations!"
              "<br/> Your login: ") + form['email']
    )


def send_email_confirmation(form, link):
    """account confirmation"""
    send_email(
        to=form['email'],
        action=USER_CONFIRM,
        subject="Email Confirmation to Create Account for Open-Event",
        html=("Hi %s<br/>" % str(form['email']) +
              "<br/> Please visit this link to confirm your email: %s" % link)
    )


def send_email_with_reset_password_hash(email, link):
    """Send email with reset password hash"""
    send_email(
        to=email,
        action=PASSWORD_RESET,
        subject="Please click to below link",
        html="Change password now " + link
    )


def send_email(to, action, subject, html):
    """
    Sends email and records it in DB
    """
    payload = {
        'to': to,
        'from': 'open-event@googlegroups.com',
        'subject': subject,
        'html': html
    }
    requests.post("https://api.sendgrid.com/api/mail.send.json",
                  data=payload,
                  headers=HEADERS)
    # record_mail(to, action, subject, html)
    mail = Mail(
        recipient=to, action=action, subject=subject,
        message=html, time=datetime.now()
    )
    from data import save_to_db
    save_to_db(mail, 'Mail Recorded')
    return


def is_event_admin(event_id, users):
    """
    :param event_id: Event id
    :param users: User id
    :return: is user admin
    """
    is_admin = False
    for user_obj in users:
        if user_obj.user.id == login.current_user.id:
            for ass in login.current_user.events_assocs:
                if ass.event_id == int(event_id):
                    is_admin = ass.admin
                    if is_event_admin:
                        return is_admin
    return is_admin


def get_serializer(secret_key=None):
    return Serializer('secret_key')


def get_latest_heroku_release():
    token = os.environ.get('API_TOKEN_HEROKU', '')
    headers = {
        "Accept": "application/vnd.heroku+json; version=3",
        "Authorization": "Bearer " + token,
        "Range": "version ..; max=1, order=desc"
    }
    response = requests.get("https://api.heroku.com/apps/open-event/releases", headers=headers)
    try:
        return json.loads(response.text)[0]
    except:
        return []


def get_commit_info(commit_number):
    response = requests.get("https://api.github.com/repos/fossasia/open-event-orga-server/commits/" + commit_number)
    return json.loads(response.text)

def string_empty(string):
    if type(string) is not str and type(string) is not unicode:
        return False
    if string and string.strip() and string != u'' and string != u' ':
        return False
    else:
        return True

def string_not_empty(string):
    return not string_empty(string)

def fields_not_empty(obj, fields):
    for field in fields:
        if string_empty(getattr(obj, field)):
            return False
    return True


def get_request_stats():
    """
    Get IP, Browser, Platform, Version etc
    http://werkzeug.pocoo.org/docs/0.11/utils/#module-werkzeug.useragents

    Note: request.remote_addr gives the server's address if the server is behind a reverse proxy. -@niranjan94
    """
    return {
        'ip': request.environ['REMOTE_ADDR'],
        'platform': request.user_agent.platform,
        'browser': request.user_agent.browser,
        'version': request.user_agent.version,
        'language': request.user_agent.language
    }
