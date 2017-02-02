from flask import Blueprint
from flask import url_for, redirect, abort, jsonify, render_template
from flask.ext import login

from app.helpers.data import DataManager
from app.helpers.data_getter import DataGetter

notifications = Blueprint('notifications', __name__, url_prefix='/notifications')


@notifications.route('/')
def index_view():
    user = login.current_user
    notifications = DataGetter.get_all_user_notifications(user)
    return render_template('gentelella/users/profile/notifications.html',
                           notifications=notifications)


@notifications.route('/read/<notification_id>/')
def mark_as_read(notification_id):
    user = login.current_user
    notification = DataGetter.get_user_notification(notification_id)

    if notification and notification.user == user:
        DataManager.mark_user_notification_as_read(notification)
        return jsonify({'status': 'ok'})
    else:
        abort(404)


@notifications.route('/allread/')
def mark_all_read():
    user = login.current_user
    DataManager.mark_all_user_notification_as_read(user)
    return redirect(url_for('.index_view'))
