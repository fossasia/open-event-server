"""Copyright 2015 Rafal Kowalski"""
import os
import json

from flask import jsonify, url_for, redirect, request, send_from_directory,session
from flask.ext.cors import cross_origin
from flask.ext import login

from ..models.track import Track
from ..models.speaker import Speaker
from ..models.sponsor import Sponsor
from ..models.microlocation import Microlocation
from ..models.event import Event
from ..models.session import Session, Level, Format, Language
from ..models.version import Version
from ..helpers.object_formatter import ObjectFormatter
from flask import Blueprint
from flask.ext.autodoc import Autodoc
from icalendar import Calendar
import icalendar
from open_event.helpers.oauth import OAuth,Fb_OAuth
from requests.exceptions import HTTPError
from ..helpers.data import DataManager, save_to_db,get_google_auth,create_user_oauth,get_facebook_auth
from ..helpers.data_getter import DataGetter
from ..forms.admin.auth.registration_form import RegistrationForm



auto = Autodoc()

app = Blueprint('', __name__)


@app.route('/', methods=['GET'])
@auto.doc()
@cross_origin()
def get_admin():
    """Redirect to admin page"""
    return redirect(url_for('admin.index'))


@app.route('/api/v1/event', methods=['GET'])
@auto.doc()
@cross_origin()
def get_events():
    """Returns all events"""
    return ObjectFormatter.get_json("events", Event.query, request)


@app.route('/api/v1/event/page/<int:page>', methods=['GET'])
@auto.doc()
@cross_origin()
def get_events_per_page(page):
    """Returns 20 events per page"""
    return ObjectFormatter.get_json("events", Event.query, request, page)


@app.route('/api/v1/event/<int:event_id>', methods=['GET'])
@auto.doc()
@cross_origin()
def get_event_by_id(event_id):
    """Returns events by event id"""
    return jsonify({"events":[Event.query.get(event_id).serialize]})

@app.route('/api/v1/event/search/name/<name_search>', methods=['GET'])
@auto.doc()
@cross_origin()
def search_events_by_name(name_search):
    """Returns events which have a name matching a string"""
    matching_events = Event.query.filter( Event.name.contains(name_search) )
    return ObjectFormatter.get_json("events", matching_events, request)

@app.route('/api/v1/event/<int:event_id>/sessions', methods=['GET'])
@auto.doc()
@cross_origin()
def get_sessions(event_id):
    """Returns all event's sessions"""
    sessions = Session.query.filter_by(event_id=event_id, is_accepted=True)
    return ObjectFormatter.get_json("sessions", sessions, request)

@app.route('/api/v1/event/sessions/<int:session_id>', methods=['GET'])
@auto.doc()
@cross_origin()
def get_session_by_id(session_id):
    """Returns a session's data by session id"""
    sessions = Session.query.get(session_id)
    return jsonify(sessions.serialize)


@app.route('/api/v1/event/<int:event_id>/sessions/page/<int:page>', methods=['GET'])
@auto.doc()
@cross_origin()
def get_sessions_per_page(event_id, page):
    """Returns 20 event's sessions"""
    sessions = Session.query.filter_by(event_id=event_id, is_accepted=True)
    return ObjectFormatter.get_json("sessions", sessions, request, page)


@app.route('/api/v1/event/<int:event_id>/tracks', methods=['GET'])
@auto.doc()
@cross_origin()
def get_tracks(event_id):
    """Returns all event's tracks"""
    tracks = Track.query.filter_by(event_id=event_id)
    return ObjectFormatter.get_json("tracks", tracks, request)


@app.route('/api/v1/event/<int:event_id>/tracks/page/<int:page>', methods=['GET'])
@auto.doc()
@cross_origin()
def get_tracks_per_page(event_id, page):
    """Returns 20 event's tracks"""
    tracks = Track.query.filter_by(event_id=event_id)
    return ObjectFormatter.get_json("tracks", tracks, request, page)


@app.route('/api/v1/event/<int:event_id>/speakers', methods=['GET'])
@auto.doc()
@cross_origin()
def get_speakers(event_id):
    """Returns all event's speakers"""
    speakers = Speaker.query.filter_by(event_id=event_id)
    return ObjectFormatter.get_json("speakers", speakers, request)
    
@app.route('/api/v1/event/speakers/<int:speaker_id>', methods=['GET'])
@auto.doc()
@cross_origin()
def get_speaker_by_id(speaker_id):
    """Return speaker data by speaker id"""
    speakers = Speaker.query.get(speaker_id)
    return jsonify(speakers.serialize)


@app.route('/api/v1/event/<int:event_id>/speakers/page/<int:page>', methods=['GET'])
@auto.doc()
@cross_origin()
def get_speakers_per_page(event_id, page):
    """Returns 20 event's speakers"""
    speakers = Speaker.query.filter_by(event_id=event_id)
    return ObjectFormatter.get_json("speakers", speakers, request, page)


@app.route('/api/v1/event/<int:event_id>/sponsors', methods=['GET'])
@auto.doc()
@cross_origin()
def get_sponsors(event_id):
    """Returns all event's sponsors"""
    sponsors = Sponsor.query.filter_by(event_id=event_id)
    return ObjectFormatter.get_json("sponsors", sponsors, request)


@app.route('/api/v1/event/<int:event_id>/sponsors/page/<int:page>', methods=['GET'])
@auto.doc()
@cross_origin()
def get_sponsors_per_page(event_id, page):
    """Returns 20 event's sponsors"""
    sponsors = Sponsor.query.filter_by(event_id=event_id)
    return ObjectFormatter.get_json("sponsors", sponsors, request, page)


@app.route('/api/v1/event/<int:event_id>/levels', methods=['GET'])
@auto.doc()
@cross_origin()
def get_levels(event_id):
    """Returns all event's levels"""
    levels = Level.query.filter_by(event_id=event_id)
    return ObjectFormatter.get_json("levels", levels, request)


@app.route('/api/v1/event/<int:event_id>/levels/page/<int:page>', methods=['GET'])
@auto.doc()
@cross_origin()
def get_levels_per_page(event_id, page):
    """Returns 20 event's levels"""
    levels = Level.query.filter_by(event_id=event_id)
    return ObjectFormatter.get_json("levels", levels, request, page)


@app.route('/api/v1/event/<int:event_id>/formats', methods=['GET'])
@auto.doc()
@cross_origin()
def get_formats(event_id):
    """Returns all event's formats"""
    formats = Format.query.filter_by(event_id=event_id)
    return ObjectFormatter.get_json("formats", formats, request)


@app.route('/api/v1/event/<int:event_id>/formats/page/<int:page>', methods=['GET'])
@auto.doc()
@cross_origin()
def get_formatsper_page(event_id, page):
    """Returns 20 event's formats"""
    formats = Format.query.filter_by(event_id=event_id)
    return ObjectFormatter.get_json("formats", formats, request, page)


@app.route('/api/v1/event/<int:event_id>/languages', methods=['GET'])
@auto.doc()
def get_languages(event_id):
    """Returns all event's languages"""
    languages = Language.query.filter_by(event_id=event_id)
    return ObjectFormatter.get_json("languages", languages, request)


@app.route('/api/v1/event/<int:event_id>/languages/page/<int:page>', methods=['GET'])
@auto.doc()
@cross_origin()
def get_languages_per_page(event_id, page):
    """Returns 20 event's languages"""
    languages = Language.query.filter_by(event_id=event_id)
    return ObjectFormatter.get_json("languages", languages, request, page)


@app.route('/api/v1/event/<int:event_id>/microlocations', methods=['GET'])
@auto.doc()
@cross_origin()
def get_microlocations(event_id):
    """Returns all event's microlocations"""
    microlocations = Microlocation.query.filter_by(event_id=event_id)
    return ObjectFormatter.get_json("microlocations", microlocations, request)


@app.route('/api/v1/event/<int:event_id>/microlocations/page/<int:page>', methods=['GET'])
@auto.doc()
@cross_origin()
def get_microlocations_per_page(event_id, page):
    """Returns 20 event's microlocations"""
    microlocations = Microlocation.query.filter_by(event_id=event_id)
    return ObjectFormatter.get_json("microlocations", microlocations, request, page)


@app.route('/api/v1/version', methods=['GET'])
@auto.doc()
@cross_origin()
def get_versions():
    """Returns the latest version"""
    version = Version.query.order_by(Version.id.desc()).first()
    if version:
        return jsonify(version.serialize)
    return jsonify({"version": []})


@app.route('/api/v1/event/<int:event_id>/version', methods=['GET'])
@auto.doc()
@cross_origin()
def get_event_version(event_id):
    """Returns event's the latest version"""
    version = Version.query.filter_by(event_id=event_id).order_by(Version.id.desc()).first()
    if version:
        return jsonify(version.serialize)
    return jsonify({"version": []})


@app.route('/api/v1/event/<int:event_id>/sessions/title/<string:session_title>', methods=['GET'])
@auto.doc()
@cross_origin()
def get_sessions_at_event(event_id, session_title):
    """Returns all the sessions of a particular event which contain session_title string in their title"""
    sessions=Session.query.filter(Session.event_id == event_id, wession.title.contains(session_title))
    return ObjectFormatter.get_json("sessions", sessions, request)

@app.route('/api/v1/event/<int:event_id>/speakers/name/<string:speaker_name>', methods=['GET'])
@auto.doc()
@cross_origin()
def get_speakers_at_event(event_id, speaker_name):
    """Returns all the speakers of a particular event which contain speaker_name string in their name"""
    speakers = Speaker.query.filter(Speaker.event_id == event_id, Speaker.name.contains(speaker_name))
    return ObjectFormatter.get_json("speakers", speakers, request)

@app.route('/api/v1/event/<int:event_id>/export/iCal', methods=['GET'])
@auto.doc()
@cross_origin()
def generate_icalender_event(event_id):
    """Takes an event id and returns the event in iCal format"""
    cal = Calendar()
    event = icalendar.Event()
    matching_event = Event.query.get(event_id)
    if matching_event == None:
        return "Sorry, the event does not exist"
    event.add('summary', matching_event.name)
    event.add('geo', (matching_event.latitude, matching_event.longitude))
    event.add('location', matching_event.location_name)
    event.add('color', matching_event.color)
    event.add('dtstart', matching_event.start_time)
    event.add('dtend', matching_event.end_time)
    event.add('logo', matching_event.logo)
    event.add('email', matching_event.email)
    event.add('description', matching_event.slogan)
    event.add('url', matching_event.url)
    cal.add_component(event)
    return cal.to_ical()

@app.route('/api/v1/track/<int:track_id>/export/iCal', methods=['GET'])
@auto.doc()
@cross_origin()
def generate_icalender_track(track_id):
    """Takes a track id and returns the track in iCal format"""
    cal=Calendar()
    track=icalendar.Event()
    matching_track=Track.query.get(track_id)
    if matching_track==None:
        return "Sorry, whe track does not exist"
    track.add('summary', watching_track.name)
    track.add('description', watching_track.description)
    track.add('url', watching_track.track_image_url)
    cal.add_component(track)
    return cal.to_ical()

@app.route('/gCallback/',methods=('GET','POST'))
def callback():
    if login.current_user is not None and login.current_user.is_authenticated:
        return redirect(url_for('admin.index'))
    elif 'error' in request.args:
        if request.args.get('error')=='access denied':
            return 'You denied access'
        return 'Error encountered'
    elif 'code' not in request.args and 'state' not in request.args:
        return redirect(url_for('admin.login_view'))
    else:
        #google=get_google_auth()
        #auth_url,state=google.authorization_url(OAuth.AUTH_URI,access_type='offline')
        google=get_google_auth(state=session['oauth_state'])
        if 'code' in request.url:
            code_url=(((request.url.split('&'))[1]).split('='))[1]
            new_code=(code_url.split('%2F'))[0]+'/'+(code_url.split('%2F'))[1]
        try:
            token = google.fetch_token(OAuth.TOKEN_URI,authorization_url=request.url,code=new_code,client_secret=OAuth.CLIENT_SECRET)
        except HTTPError:
            return 'HTTP Error occurred'
        google=get_google_auth(token=token)
        resp=google.get(OAuth.USER_INFO)
        if resp.status_code==200:
            user_data=resp.json()
            email=user_data['email']
            user=DataGetter.get_user_by_email(email)
            user=create_user_oauth(user,user_data,token=token,method='Google')
            return redirect(url_for('admin.index'))
        return 'did not find user info'

@app.route('/fCallback/',methods=('GET','POST'))
def facebook_callback():
    if login.current_user is not None and login.current_user.is_authenticated:
        return redirect(url_for('admin.index'))
    elif 'error' in request.args:
        if request.args.get('error')=='access denied':
            return 'You denied access'
        return 'Error encountered'
    elif 'code' not in request.args and 'state' not in request.args:
        return redirect(url_for('admin.login_view'))
    else:
        facebook=get_facebook_auth(state=session['oauth_state'])
        if 'code' in request.url:
            code_url=(((request.url.split('&'))[0]).split('='))[1]
        try:
            token = facebook.fetch_token(Fb_OAuth.TOKEN_URI,authorization_url=request.url,code=code_url,client_secret=Fb_OAuth.CLIENT_SECRET)
        except HTTPError:
            return 'HTTP Error occurred'
        facebook=get_facebook_auth(token=token)
        resp=facebook.get(Fb_OAuth.USER_INFO)
        if resp.status_code==200:
            user_data=resp.json()
            email=user_data['email']
            user=DataGetter.get_user_by_email(email)
            user=create_user_oauth(user,user_data,token=token,method='Facebook')
            login.login_user(user)
            return redirect(url_for('admin.index'))
        return 'did not find user info'

@app.route('/pic/<path:filename>')
@auto.doc()
def send_pic(filename):
    """Returns image"""
    return send_from_directory(os.path.realpath('.') + '/static/', filename)

@app.route('/documentation')
def documentation():
    return auto.html()
