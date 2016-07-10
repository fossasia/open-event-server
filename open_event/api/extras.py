"""
This file contains API v2 endpoints that are too small to be written as
individual modules
OR
that are not important to the end-user
"""

from flask.ext.restplus import Resource, Namespace
from celery.result import AsyncResult
from flask import jsonify

from helpers.errors import BaseError, ServerError


api = Namespace('extras', description='Extras', path='/')


@api.route('/tasks/<string:task_id>')
@api.hide
class CeleryTask(Resource):
    def get(self, task_id):
        """
        Get CeleryTask status of an APIv2 based task
        """
        from open_event import celery
        result = AsyncResult(id=task_id, app=celery)
        if result.state == 'SUCCESS':
            return result.get()
        elif result.state == 'FAILURE':
            r = result.result
            if isinstance(r, BaseError):
                print r, 'hi'
                raise r
            else:
                raise ServerError()
        else:
            return jsonify(status=result.state)
