from ..helpers.data_getter import DataGetter
from flask import jsonify
import json


def error_404_message(item):
    """Make error message for non-existence of {item}"""
    return '%s does not exist' % item


def api_response(
        data=None,
        status_code=200,
        error='Item',
        check_data=False,
        error_data='Page'):
    """
    Api response helper
    if status_code is 200, return data
    else return error message with {status_code}
    """
    # check if data is empty
    if check_data:
        if len(json.loads(data.data)) == 0 and status_code == 200:
            # don't overwrite existing error
            status_code = 404
            error = error_data
    # return response
    if status_code == 200:
        return data, 200
    elif status_code == 404:
        return jsonify({"message": error_404_message(error)}), 404
    else:  # for future extensibility
        return jsonify({"message": error}), status_code


def event_status_code(event_id):
    """
    Helper function to return status code 200 if event exists
    else 404
    """
    return 200 if DataGetter.get_event(event_id) else 404
