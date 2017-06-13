from flask import Blueprint
from flask import redirect, request, url_for
from flask import render_template

from app.helpers.data import DataManager
from app.helpers.data_getter import DataGetter
from app.helpers.system_mails import MAILS
from app.helpers.system_notifications import NOTIFS
from app.views.super_admin import MESSAGES, check_accessible, list_navbar

sadmin_messages = Blueprint('sadmin_messages', __name__, url_prefix='/admin/messages')


@sadmin_messages.before_request
def verify_accessible():
    return check_accessible(MESSAGES)


@sadmin_messages.route('/')
def index_view():
    message_settings = DataGetter.get_all_message_setting()
    return render_template(
        'gentelella/super_admin/messages/messages.html',
        mails=MAILS,
        notifications=NOTIFS,
        message_settings=message_settings,
        navigation_bar=list_navbar()
    )


@sadmin_messages.route('/update/', methods=['POST'])
def update_view():
    if request.method == 'POST':
        DataManager.create_or_update_message_settings(request.form)
    return redirect(url_for('sadmin_messages.index_view'))
