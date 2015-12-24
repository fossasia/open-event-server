"""Copyright 2015 Rafal Kowalski"""
import os
from flask import jsonify, url_for, redirect, request, send_from_directory
from flask.ext.cors import cross_origin

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

auto=Autodoc()

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
def get_languages(event_id, page):
    """Returns all event's languages"""
    languages = Language.query.filter_by(event_id=event_id)
    return ObjectFormatter.get_json("languages", languages, request, page)


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
    sessions=Session.query.filter(Session.event_id == event_id,Session.title.contains(session_title))
    return ObjectFormatter.get_json("sessions", sessions, request)

@app.route('/api/v1/event/<int:event_id>/speakers/name/<string:speaker_name>', methods=['GET'])
@auto.doc()
@cross_origin()
def get_speakers_at_event(event_id, speaker_name):
    speakers=Speaker.query.filter(Speaker.event_id == event_id,Speaker.name.contains(speaker_name))
    return ObjectFormatter.get_json("speakers", speakers, request)

@app.route('/pic/<path:filename>')
@auto.doc()
def send_pic(filename):
    """Returns image"""
    return send_from_directory(os.path.realpath('.') + '/static/', filename)

@app.route('/documentation')
def documentation():
	return auto.html()
