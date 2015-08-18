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


app = Blueprint('', __name__)
@app.route('/', methods=['GET'])
@cross_origin()
def get_admin():
    return redirect(url_for('admin.index'))


@app.route('/api/v1/event', methods=['GET'], defaults={'page': 1})
@app.route('/api/v1/event/page/<int:page>', methods=['GET'])
@cross_origin()
def get_events(page):
    return ObjectFormatter.get_json("events", Event.query, request, page)


@app.route('/api/v1/event/<event_id>', methods=['GET'])
@cross_origin()
def get_event_by_id(event_id):
    return jsonify({"events":[Event.query.get(event_id).serialize]})


@app.route('/api/v1/event/<event_id>/sessions', methods=['GET'], defaults={'page': 1})
@app.route('/api/v1/event/<event_id>/sessions/page/<int:page>', methods=['GET'])
@cross_origin()
def get_sessions(event_id, page):
    sessions = Session.query.filter_by(event_id=event_id)
    return ObjectFormatter.get_json("sessions", sessions, request, page)


@app.route('/api/v1/event/<event_id>/tracks', methods=['GET'], defaults={'page': 1})
@app.route('/api/v1/event/<event_id>/tracks/page/<int:page>', methods=['GET'])
@cross_origin()
def get_tracks(event_id, page):
    tracks = Track.query.filter_by(event_id=event_id)
    return ObjectFormatter.get_json("tracks", tracks, request, page)


@app.route('/api/v1/event/<event_id>/speakers', methods=['GET'], defaults={'page': 1})
@app.route('/api/v1/event/<event_id>/speakers/page/<int:page>', methods=['GET'])
@cross_origin()
def get_speakers(event_id, page):
    speakers = Speaker.query.filter_by(event_id=event_id)
    return ObjectFormatter.get_json("speakers", speakers, request, page)


@app.route('/api/v1/event/<event_id>/sponsors', methods=['GET'], defaults={'page': 1})
@app.route('/api/v1/event/<event_id>/sponsors/page/<int:page>', methods=['GET'])
@cross_origin()
def get_sponsors(event_id, page):
    sponsors = Sponsor.query.filter_by(event_id=event_id)
    return ObjectFormatter.get_json("sponsors", sponsors, request, page)


@app.route('/api/v1/event/<event_id>/levels', methods=['GET'], defaults={'page': 1})
@app.route('/api/v1/event/<event_id>/levels/page/<int:page>', methods=['GET'])
@cross_origin()
def get_levels(event_id, page):
    levels = Level.query.filter_by(event_id=event_id)
    return ObjectFormatter.get_json("levels", levels, request, page)


@app.route('/api/v1/event/<event_id>/formats', methods=['GET'], defaults={'page': 1})
@app.route('/api/v1/event/<event_id>/formats/page/<int:page>', methods=['GET'])
@cross_origin()
def get_formats(event_id, page):
    formats = Format.query.filter_by(event_id=event_id)
    return ObjectFormatter.get_json("formats", formats, request, page)


@app.route('/api/v1/event/<event_id>/languages', methods=['GET'], defaults={'page': 1})
@app.route('/api/v1/event/<event_id>/languages/page/<int:page>', methods=['GET'])
@cross_origin()
def get_languages(event_id, page):
    languages = Language.query.filter_by(event_id=event_id)
    return ObjectFormatter.get_json("languages", languages, request, page)


@app.route('/api/v1/event/<event_id>/microlocations', methods=['GET'], defaults={'page': 1})
@app.route('/api/v1/event/<event_id>/microlocations/page/<int:page>', methods=['GET'])
@cross_origin()
def get_microlocations(event_id, page):
    microlocations = Microlocation.query.filter_by(event_id=event_id)
    return ObjectFormatter.get_json("microlocations", microlocations, request, page)


@app.route('/api/v1/version', methods=['GET'])
@cross_origin()
def get_versions():
    version = Version.query.order_by(Version.id.desc()).first()
    if version:
        return jsonify(version.serialize)
    return jsonify({"version": []})


@app.route('/api/v1/event/<event_id>/version', methods=['GET'])
@cross_origin()
def get_event_version(event_id):
    version = Version.query.filter_by(event_id=event_id).order_by(Version.id.desc()).first()
    if version:
        return jsonify(version.serialize)
    return jsonify({"version": []})


@app.route('/pic/<path:filename>')
def send_pic(filename):
    return send_from_directory(os.path.realpath('.') + '/static/', filename)