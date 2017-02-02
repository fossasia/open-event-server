import unicodedata

from flask import Blueprint, render_template
from flask import request, url_for, redirect, jsonify, flash
from flask.ext import login
from flask.ext.scrypt import generate_password_hash, generate_random_salt

from app.helpers.data import DataManager, save_to_db
from app.helpers.data_getter import DataGetter
from app.models.email_notifications import EmailNotification
from app.views.home import record_user_login_logout


def get_or_create_notification_settings(event_id):
    email_notification = DataGetter \
        .get_email_notification_settings_by_event_id(login.current_user.id, event_id)
    if email_notification:
        return email_notification
    else:
        email_notification = EmailNotification(next_event=1,
                                               new_paper=1,
                                               session_schedule=1,
                                               session_accept_reject=1,
                                               after_ticket_purchase=1,
                                               user_id=login.current_user.id,
                                               event_id=event_id)
        return email_notification


settings = Blueprint('settings', __name__, url_prefix='/settings')


@settings.route('/')
def index_view():
    return redirect(url_for('.contact_info_view'))


@settings.route('/password/', methods=('POST', 'GET'))
def password_view():
    if request.method == 'POST':
        user = login.current_user
        if user.password == generate_password_hash(request.form['current_password'], user.salt):
            if request.form['new_password'] == request.form['repeat_password']:
                salt = generate_random_salt()
                user.password = generate_password_hash(request.form['new_password'], salt)
                user.salt = salt
                save_to_db(user, "password changed")
                record_user_login_logout('user_logout', login.current_user)
                login.logout_user()
                flash('Your password has been changed. Please login with your new password now.', 'success')
                return redirect(url_for('admin.login_view'))
            else:
                flash('The new password and the repeat don\'t match.', 'danger')
        else:
            flash('The current password is incorrect.', 'danger')

    return render_template('gentelella/users/settings/pages/password.html')


@settings.route('/email-preferences/')
def email_preferences_view():
    events = DataGetter.get_all_events()
    message_settings = DataGetter.get_all_message_setting()
    settings = DataGetter.get_email_notification_settings(login.current_user.id)
    user = DataGetter.get_user(login.current_user.id)
    return render_template('gentelella/users/settings/pages/email_preferences.html',
                           settings=settings, events=events, message_settings=message_settings, user=user)


@settings.route('/applications/')
def applications_view():
    user = DataGetter.get_user(login.current_user.id)
    return render_template('gentelella/users/settings/pages/applications.html',
                           user=user)


@settings.route('/contact-info/', methods=('POST', 'GET'))
def contact_info_view():
    user_id = login.current_user.id
    if request.method == 'POST':
        DataManager.update_user(request.form, int(user_id), contacts_only_update=True)
        flash("Your contact info has been updated.", "success")
        return redirect(url_for('.contact_info_view'))
    profile = DataGetter.get_user(int(user_id))

    return render_template('gentelella/users/settings/pages/contact_info.html', user=login.current_user)


@settings.route('/email/toggle/', methods=('POST',))
def email_toggle_view():
    if request.method == 'POST':
        name = request.form.get('name')
        value = int(request.form.get('value'))
        event_id = request.form.get('event_id')

        message = ''

        if name == 'global_email':
            ids = DataManager.toggle_email_notification_settings(login.current_user.id, value)
        else:
            name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore')
            email_notification = get_or_create_notification_settings(event_id)
            setattr(email_notification, name, value)
            save_to_db(email_notification, "EmailSettings Toggled")
            ids = [email_notification.id]

        return jsonify({
            'status': 'ok',
            'message': message,
            'notification_setting_ids': ids
        })
