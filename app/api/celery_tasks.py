"""
This API is meant to store the Task Result for a celery task
and used for purposes such as polling
"""
from celery.result import AsyncResult
from flask import Blueprint, current_app, jsonify

from app.api.helpers.utilities import TASK_RESULTS

celery_routes = Blueprint('tasks', __name__, url_prefix='/v1')


@celery_routes.route('/tasks/<string:task_id>')
def celery_task(task_id):
    """
    Get CeleryTask status of an API based task
    """
    # in case of always eager, get results. don't call AsyncResult
    # which rather looks in redis
    if current_app.config.get('CELERY_ALWAYS_EAGER'):
        state = TASK_RESULTS[task_id]['state']
        info = TASK_RESULTS[task_id]['result']
    else:
        from app.api.helpers.tasks import celery

        result = AsyncResult(id=task_id, app=celery)
        state = result.state
        info = result.info
    # check
    if state == 'SUCCESS':
        if type(info) is dict:
            # check if is error
            if '__error' in info:
                return jsonify(state='FAILURE', result=info['result'])
            # return normal
        return jsonify(state=state, result=info)
    return jsonify(state=state)
