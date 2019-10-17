from flask import jsonify, Blueprint
from datetime import datetime

SERVER_VERSION = '2.2.3-SNAPSHOT'

info_route = Blueprint('info', __name__, url_prefix='/v1')
_build = {'time': str(datetime.now()), 'version': SERVER_VERSION}


class ServerVersion:

    @staticmethod
    @info_route.route('/info')
    def version():
        return jsonify(build=_build)
