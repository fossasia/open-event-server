"""
This API is meant to store the Task Result for a celery task
and used for purposes such as polling
"""
from celery.result import AsyncResult
from flask import jsonify, current_app, Blueprint
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
        from app.views.celery_ import celery
        result = AsyncResult(id=task_id, app=celery)
        state = result.state
        info = result.info
    # check
    if state == 'SUCCESS':
        if type(info) == dict:
            # check if is error
            if '__error' in info:
                return info['result']
        # return normal
        return jsonify(state='SUCCESS', result=info)
    elif state == 'FAILURE':
        return jsonify(state=state)
    else:
        return jsonify(state=state)
