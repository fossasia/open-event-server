import sys
import logging

from flask import Flask, render_template, jsonify, url_for
from flask import request
from flask.ext.cors import CORS, cross_origin
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager

from open_event.views.admin.admin import AdminView
from open_event.models import db
from open_event.models.track import Track
from open_event.models.speaker import Speaker
from open_event.models.sponsor import Sponsor
from open_event.models.microlocation import Microlocation
from open_event.models.event import Event
from open_event.models.session import Session
from helpers.query_filter import QueryFilter

app = Flask(__name__)
migrate = Migrate(app, db)
cors = CORS(app)
app.secret_key = 'super secret key'
app.config.from_object('config')
manager = Manager(app)
manager.add_command('db', MigrateCommand)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

AdminView(app, "Open Event").init()

db.init_app(app)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.route('/get/api/v1/event', methods=['GET'])
@cross_origin()
def get_events():
    return jsonify({"events":
                    [event.serialize for event in QueryFilter(request.args, Event.query).get_filtered_data()]})


@app.route('/get/api/v1/event/<event_id>', methods=['GET'])
@cross_origin()
def get_event_by_id(event_id):
    return jsonify(Event.query.get(event_id).serialize)


@app.route('/get/api/v1/event/<event_id>/sessions', methods=['GET'])
@cross_origin()
def get_sessions(event_id):
    sessions = Track.query.filter_by(event_id=event_id)
    return jsonify({"sessions":
                    [session.serialize for session in QueryFilter(request.args, sessions).get_filtered_data()]})


@app.route('/get/api/v1/event/<event_id>/tracks', methods=['GET'])
@cross_origin()
def get_tracks(event_id):
    tracks = Track.query.filter_by(event_id=event_id)
    return jsonify({"tracks":
                    [track.serialize for track in QueryFilter(request.args, tracks).get_filtered_data()]})


@app.route('/get/api/v1/event/<event_id>/speakers', methods=['GET'])
@cross_origin()
def get_speakers(event_id):
    speakers = Track.query.filter_by(event_id=event_id)
    return jsonify({"speakers":
                    [speaker.serialize for speaker in QueryFilter(request.args, speakers).get_filtered_data()]})


@app.route('/get/api/v1/event/<event_id>/sponsors', methods=['GET'])
@cross_origin()
def get_sponsors(event_id):
    sponsors = Sponsor.query.filter_by(event_id=event_id)
    return jsonify({"sponsors":
                    [sponsor.serialize for sponsor in QueryFilter(request.args, sponsors).get_filtered_data()]})


@app.route('/get/api/v1/event/<event_id>/microlocations', methods=['GET'])
@cross_origin()
def get_microlocations(event_id):
    microlocations = Microlocation.query.filter_by(event_id=event_id)
    return jsonify({"microlocations":
                    [microlocation.serialize for microlocation in QueryFilter(request.args, microlocations).get_filtered_data()]})


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