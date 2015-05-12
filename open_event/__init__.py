from flask import Flask, render_template, jsonify
from open_event.models import Event, Session, Track, Speaker, Sponsor, Microlocation,db
from admin import AdminView

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
                    [event.serialize for event in Event.query.all()]})

@app.route('/get/api/v1/sessions', methods=['GET'])
def get_sessions():
    return jsonify({"sessions":
                    [session.serialize for session in Session.query.all()]})

@app.route('/get/api/v1/tracks', methods=['GET'])
def get_tracks():
    return jsonify({"tracks":
                    [track.serialize for track in Track.query.all()]})

@app.route('/get/api/v1/speakers', methods=['GET'])
def get_speakers():
    return jsonify({"speakers":
                    [speaker.serialize for speaker in Speaker.query.all()]})

@app.route('/get/api/v1/sponsors', methods=['GET'])
def get_sponsors():
    return jsonify({"sponsors":
                    [sponsor.serialize for sponsor in Sponsor.query.all()]})

@app.route('/get/api/v1/microlocations', methods=['GET'])
def get_microlocations():
    return jsonify({"microlocation":
                    [microlocation.serialize for microlocation in Microlocation.query.all()]})


