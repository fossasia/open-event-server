from flask import jsonify, Blueprint


SERVER_VERSION = '1.0'

server_version_route = Blueprint('server_version', __name__, url_prefix='/v1')


class ServerVersion:
    @staticmethod
    @server_version_route.route('/server_version')
    def version():
        return jsonify(server_version=SERVER_VERSION)
