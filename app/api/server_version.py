from flask import Blueprint, current_app, jsonify

info_route = Blueprint('info', __name__)


@info_route.route('/info')
def version():
    return jsonify(build={'version': current_app.config['VERSION']})
