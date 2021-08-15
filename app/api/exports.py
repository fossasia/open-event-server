import os

from flask import (
    Blueprint,
    current_app,
    jsonify,
    make_response,
    request,
    send_file,
    url_for,
)
from flask_jwt_extended import current_user

from app.api.helpers.export_helpers import create_export_job, export_event_json
from app.api.helpers.permissions import is_admin, is_coorganizer, to_event_id
from app.api.helpers.utilities import TASK_RESULTS

export_routes = Blueprint('exports', __name__, url_prefix='/v1')

EXPORT_SETTING = {'image': False, 'video': False, 'document': False, 'audio': False}


@export_routes.route(
    '/events/<string:event_identifier>/export/json',
    methods=['POST'],
    endpoint='export_event',
)
@to_event_id
@is_coorganizer
def export_event(event_id):
    from .helpers.tasks import export_event_task

    settings = EXPORT_SETTING
    settings['image'] = request.json.get('image', False)
    settings['video'] = request.json.get('video', False)
    settings['document'] = request.json.get('document', False)
    settings['audio'] = request.json.get('audio', False)

    # queue task
    task = export_event_task.delay(current_user.email, event_id, settings)
    # create Job
    create_export_job(task.id, event_id)

    # in case of testing
    if current_app.config.get('CELERY_ALWAYS_EAGER'):
        # send_export_mail(event_id, task.get())
        TASK_RESULTS[task.id] = {'result': task.get(), 'state': task.state}
    return jsonify(task_url=url_for('tasks.celery_task', task_id=task.id))


@export_routes.route(
    '/events/<string:event_id>/exports/<path:path>', endpoint='export_download'
)
@to_event_id
@is_coorganizer
def export_download(event_id, path):
    if not path.startswith('/'):
        path = '/' + path
    if not os.path.isfile(path):
        return 'Not Found', 404
    response = make_response(send_file(path))
    response.headers['Content-Disposition'] = (
        'attachment; filename=event%d.zip' % event_id
    )
    return response


@export_routes.route(
    '/events/<string:event_identifier>/export/xcal',
    methods=['GET'],
    endpoint='export_event_xcal',
)
@to_event_id
@is_coorganizer
def export_event_xcal(event_id):

    from .helpers.tasks import export_xcal_task

    # queue task
    task = export_xcal_task.delay(event_id)
    # create Job
    create_export_job(task.id, event_id)

    return jsonify(task_url=url_for('tasks.celery_task', task_id=task.id))


def event_export_task_base(event_id, settings):
    path = export_event_json(event_id, settings)
    if path.startswith('/'):
        path = path[1:]
    return path


@export_routes.route(
    '/events/<string:event_identifier>/export/ical',
    methods=['GET'],
    endpoint='export_event_ical',
)
@to_event_id
@is_coorganizer
def export_event_ical(event_id):
    from .helpers.tasks import export_ical_task

    task = export_ical_task.delay(event_id)

    create_export_job(task.id, event_id)

    return jsonify(task_url=url_for('tasks.celery_task', task_id=task.id))


@export_routes.route(
    '/events/<string:event_identifier>/export/pentabarf',
    methods=['GET'],
    endpoint='export_event_pentabarf',
)
@to_event_id
@is_coorganizer
def export_event_pentabarf(event_id):
    from .helpers.tasks import export_pentabarf_task

    task = export_pentabarf_task.delay(event_id)

    create_export_job(task.id, event_id)

    return jsonify(task_url=url_for('tasks.celery_task', task_id=task.id))


@export_routes.route(
    '/events/<string:event_identifier>/export/orders/csv',
    methods=['GET'],
    endpoint='export_orders_csv',
)
@to_event_id
@is_coorganizer
def export_orders_csv(event_id):
    from .helpers.tasks import export_order_csv_task

    task = export_order_csv_task.delay(event_id)

    create_export_job(task.id, event_id)

    return jsonify(task_url=url_for('tasks.celery_task', task_id=task.id))


@export_routes.route(
    '/events/<string:event_identifier>/export/orders/pdf',
    methods=['GET'],
    endpoint='export_orders_pdf',
)
@to_event_id
@is_coorganizer
def export_orders_pdf(event_id):
    from .helpers.tasks import export_order_pdf_task

    task = export_order_pdf_task.delay(event_id)

    create_export_job(task.id, event_id)

    return jsonify(task_url=url_for('tasks.celery_task', task_id=task.id))


@export_routes.route(
    '/events/<string:event_identifier>/export/attendees/csv',
    methods=['GET'],
    endpoint='export_attendees_csv',
)
@to_event_id
@is_coorganizer
def export_attendees_csv(event_id):
    from .helpers.tasks import export_attendees_csv_task

    task = export_attendees_csv_task.delay(event_id)

    create_export_job(task.id, event_id)

    return jsonify(task_url=url_for('tasks.celery_task', task_id=task.id))


@export_routes.route(
    '/events/<string:event_identifier>/export/attendees/pdf',
    methods=['GET'],
    endpoint='export_attendees_pdf',
)
@to_event_id
@is_coorganizer
def export_attendees_pdf(event_id):
    from .helpers.tasks import export_attendees_pdf_task

    task = export_attendees_pdf_task.delay(event_id)

    create_export_job(task.id, event_id)

    return jsonify(task_url=url_for('tasks.celery_task', task_id=task.id))


@export_routes.route(
    '/events/<string:event_identifier>/export/sessions/csv',
    methods=['POST'],
    endpoint='export_sessions_csv',
)
@to_event_id
@is_coorganizer
def export_sessions_csv(event_id):
    from .helpers.tasks import export_sessions_csv_task

    status = request.json.get('status')

    task = export_sessions_csv_task.delay(event_id, status)

    create_export_job(task.id, event_id)

    return jsonify(task_url=url_for('tasks.celery_task', task_id=task.id))


@export_routes.route(
    '/admin/export/sales/csv',
    methods=['POST'],
    endpoint='export_sales_csv',
)
@is_admin
def export_sales_csv():
    from .helpers.tasks import export_admin_sales_csv_task

    status = request.json.get('status')
    task = export_admin_sales_csv_task.delay(status)

    # here using event_id zero for admin export tasks
    event_id = 0
    create_export_job(task.id, event_id)

    return jsonify(task_url=url_for('tasks.celery_task', task_id=task.id))


@export_routes.route(
    '/events/<string:event_identifier>/export/speakers/csv',
    methods=['POST'],
    endpoint='export_speakers_csv',
)
@to_event_id
@is_coorganizer
def export_speakers_csv(event_id):
    from .helpers.tasks import export_speakers_csv_task

    status = request.json.get('status')

    task = export_speakers_csv_task.delay(event_id, status)

    create_export_job(task.id, event_id)

    return jsonify(task_url=url_for('tasks.celery_task', task_id=task.id))


@export_routes.route(
    '/group/<int:group_id>/export/followers/csv',
    methods=['POST'],
    endpoint='export_group_followers_csv',
)
def export_group_followers_csv(group_id):
    from .helpers.tasks import export_group_followers_csv_task

    task = export_group_followers_csv_task.delay(group_id)

    return jsonify(task_url=url_for('tasks.celery_task', task_id=task.id))


@export_routes.route(
    '/events/<string:event_identifier>/export/sessions/pdf',
    methods=['GET'],
    endpoint='export_sessions_pdf',
)
@to_event_id
@is_coorganizer
def export_sessions_pdf(event_id):
    from .helpers.tasks import export_sessions_pdf_task

    task = export_sessions_pdf_task.delay(event_id)

    create_export_job(task.id, event_id)

    return jsonify(task_url=url_for('tasks.celery_task', task_id=task.id))


@export_routes.route(
    '/events/<string:event_identifier>/export/speakers/pdf',
    methods=['GET'],
    endpoint='export_speakers_pdf',
)
@to_event_id
@is_coorganizer
def export_speakers_pdf(event_id):
    from .helpers.tasks import export_speakers_pdf_task

    task = export_speakers_pdf_task.delay(event_id)

    create_export_job(task.id, event_id)

    return jsonify(task_url=url_for('tasks.celery_task', task_id=task.id))
