"""Written by - Rafal Kowalski"""
from .. import app
from flask import jsonify, url_for
from flask import request
from flask.ext.cors import cross_origin

from ..models.track import Track
from ..models.speaker import Speaker
from ..models.sponsor import Sponsor
from ..models.microlocation import Microlocation
from ..models.event import Event
from ..models.session import Session
from ..models.version import Version
from ..helpers.object_formatter import ObjectFormatter

# @app.errorhandler(404)
# def not_found(error):
#     return render_template('404.html'), 404


@app.route('/get/api/v1/event', methods=['GET'])
@cross_origin()
def get_events():
    return ObjectFormatter.get_json("events", Event.query, request)


@app.route('/get/api/v1/event/<event_id>', methods=['GET'])
@cross_origin()
def get_event_by_id(event_id):
    return jsonify(Event.query.get(event_id).serialize)


@app.route('/get/api/v1/event/<event_id>/sessions', methods=['GET'])
@cross_origin()
def get_sessions(event_id):
    sessions = Track.query.filter_by(event_id=event_id)
    return ObjectFormatter.get_json("sessions", sessions, request)


@app.route('/get/api/v1/event/<event_id>/tracks', methods=['GET'])
@cross_origin()
def get_tracks(event_id):
    tracks = Track.query.filter_by(event_id=event_id)
    return ObjectFormatter.get_json("tracks", tracks, request)


@app.route('/get/api/v1/event/<event_id>/speakers', methods=['GET'])
@cross_origin()
def get_speakers(event_id):
    speakers = Track.query.filter_by(event_id=event_id)
    return ObjectFormatter.get_json("speakers", speakers, request)


@app.route('/get/api/v1/event/<event_id>/sponsors', methods=['GET'])
@cross_origin()
def get_sponsors(event_id):
    sponsors = Sponsor.query.filter_by(event_id=event_id)
    return ObjectFormatter.get_json("sponsors", sponsors, request)


@app.route('/get/api/v1/event/<event_id>/microlocations', methods=['GET'])
@cross_origin()
def get_microlocations(event_id):
    microlocations = Microlocation.query.filter_by(event_id=event_id)
    return ObjectFormatter.get_json("microlocations", microlocations, request)


@app.route('/get/api/v1/version/<event_id>', methods=['GET'])
@cross_origin()
def get_event_versions(event_id):
    versions = Version.query.filter_by(event_id=event_id)
    return ObjectFormatter.get_json("versions", versions, request)


@app.route('/get/api/v1/version', methods=['GET'])
@cross_origin()
def get_versions():
    return ObjectFormatter.get_json("versions", Version.query, request)


@app.route("/site-map")
def site_map():
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint)
            links.append((url, rule.endpoint))
    return str(links)


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)
