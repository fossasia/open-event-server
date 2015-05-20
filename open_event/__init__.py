from flask import Flask, render_template, jsonify
from open_event.models import Event, Session, Track, Speaker, Sponsor, Microlocation, db
from admin import AdminView
from flask import request
from helpers.query_filter import QueryFilter
app = Flask(__name__)
app.secret_key = 'super secret key'
app.config.from_object('config')

AdminView(app, "Open Event").init()

db.init_app(app)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.route('/get/api/v1/events', methods=['GET'])
def get_events():
    return jsonify({"events":
                    [event.serialize for event in QueryFilter(request.args, Event.query).get_filtered_data()]})


@app.route('/get/api/v1/sessions', methods=['GET'])
def get_sessions():
    return jsonify({"sessions":
                    [session.serialize for session in QueryFilter(request.args, Session.query).get_filtered_data()]})


@app.route('/get/api/v1/tracks', methods=['GET'])
def get_tracks():
    return jsonify({"tracks":
                    [track.serialize for track in QueryFilter(request.args, Track.query).get_filtered_data()]})


@app.route('/get/api/v1/speakers', methods=['GET'])
def get_speakers():
    return jsonify({"speakers":
                    [speaker.serialize for speaker in QueryFilter(request.args, Speaker.query).get_filtered_data()]})


@app.route('/get/api/v1/sponsors', methods=['GET'])
def get_sponsors():
    return jsonify({"sponsors":
                    [sponsor.serialize for sponsor in QueryFilter(request.args, Sponsor.query).get_filtered_data()]})


@app.route('/get/api/v1/microlocations', methods=['GET'])
def get_microlocations():
    return jsonify({"microlocation":
                    [microlocation.serialize for microlocation in QueryFilter(request.args, Microlocation.query).get_filtered_data()]})
