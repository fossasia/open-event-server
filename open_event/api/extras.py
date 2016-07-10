"""
This file contains API v2 endpoints that are too small to be written as
individual modules
OR
that are not important to the end-user
"""

from flask.ext.restplus import Resource, Namespace
from celery.result import AsyncResult
from flask import jsonify

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
            if type(result.info) == dict:
                # check if is error
                if '__error' in result.info:
                    return result.info['result'], result.info['result']['code']
            # return normal
            return jsonify(state='SUCCESS', result=result.get())
        elif result.state == 'FAILURE':
            return jsonify(state=result.state)
        else:
            return jsonify(state=result.state)
