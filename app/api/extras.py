"""
This file contains API v2 endpoints that are too small to be written as
individual modules
OR
that are not important to the end-user
"""

from flask.ext.restplus import Resource, Namespace
from celery.result import AsyncResult
from flask import jsonify, current_app

from .helpers.utils import TASK_RESULTS


api = Namespace('extras', description='Extras', path='/')


@api.route('/tasks/<string:task_id>')
@api.hide
class CeleryTask(Resource):
    def get(self, task_id):
        """
        Get CeleryTask status of an APIv2 based task
        """
        # in case of always eager, get results. don't call AsyncResult
        # which rather looks in redis
        if current_app.config.get('CELERY_ALWAYS_EAGER'):
            state = TASK_RESULTS[task_id]['state']
            info = TASK_RESULTS[task_id]['result']
        else:
            from app import celery
            result = AsyncResult(id=task_id, app=celery)
            state = result.state
            info = result.info
        # check
        if state == 'SUCCESS':
            if type(info) == dict:
                # check if is error
                if '__error' in info:
                    return info['result'], info['result']['code']
            # return normal
            return jsonify(state='SUCCESS', result=info)
        elif state == 'FAILURE':
            return jsonify(state=state)
        else:
            return jsonify(state=state)
