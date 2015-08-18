"""Copyright 2015 Rafal Kowalski"""
from flask import jsonify

from .query_filter import QueryFilter


class ObjectFormatter(object):

    @staticmethod
    def get_json(name, query, request, page=None):
        if not page:
            return jsonify(
                {name: [
                    table_object.serialize
                    for table_object in
                    QueryFilter(request.args, query).get_filtered_data()]})
        else:
            return jsonify(
                {name: [
                    table_object.serialize
                    for table_object in
                    QueryFilter(request.args, query).get_filtered_data().paginate(page, 50).items
                    ]})