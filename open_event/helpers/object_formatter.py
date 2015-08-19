"""Copyright 2015 Rafal Kowalski"""
from flask import jsonify

from .query_filter import QueryFilter

PER_PAGE = 20
class ObjectFormatter(object):

    @staticmethod
    def get_json(name, query, request, page=None):
        objects = QueryFilter(request.args, query).get_filtered_data()
        count = objects.count()
        if not page:
            return jsonify(
                {name: [
                    table_object.serialize
                    for table_object in
                    objects],
                 'count': count})
        else:
            pagination = objects.paginate(page, PER_PAGE)
            return jsonify(
                {name: [
                    table_object.serialize
                    for table_object in
                    pagination.items
                    ],
                  'count': count,
                  'total_pages': pagination.pages,
                  'page': pagination.page

                 })