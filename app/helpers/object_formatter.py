from flask import jsonify

from app.helpers.helpers import get_count
from .query_filter import QueryFilter

PER_PAGE = 20


class ObjectFormatter(object):
    """Object formatter class"""

    @staticmethod
    def get_json(name, query, request, page=None):
        """Returns formatted json"""
        objects = QueryFilter(request.args, query).get_filtered_data()
        count = get_count(objects)
        if not page:
            return jsonify(
                {name: [
                    table_object.serialize
                    for table_object in
                    objects]})
        else:
            if count <= ((page - 1) * PER_PAGE):  # no results possible
                return jsonify({})
            pagination = objects.paginate(page, PER_PAGE)
            return jsonify({
                name: [
                    table_object.serialize
                    for table_object in
                    pagination.items
                    ],
                'total_pages': pagination.pages,
                'page': pagination.page
            })
