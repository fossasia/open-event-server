"""Written by - Rafal Kowalski"""
from .query_filter import QueryFilter
from flask import jsonify


class ObjectFormatter(object):

    @staticmethod
    def get_json(name, query, request):
        return jsonify(
            {name: [
                table_object.serialize
                for table_object in
                QueryFilter(request.args, query).get_filtered_data()]})
