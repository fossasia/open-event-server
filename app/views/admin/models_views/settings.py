import unicodedata
from flask import request, url_for, redirect, jsonify, flash
from flask.ext.admin import BaseView
from flask.ext.scrypt import generate_password_hash, generate_random_salt
from flask_admin import expose
from flask.ext import login

from app.helpers.data import DataManager, save_to_db
from app.models.email_notifications import EmailNotification
from ....helpers.data_getter import DataGetter

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
                                               user_id=login.current_user.id,
                                               event_id=event_id)
        return email_notification


class SettingsView(BaseView):
    def is_accessible(self):
        return login.current_user.is_authenticated

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('admin.login_view', next=request.url))

    @expose('/')
    def index_view(self):
        # TODO Settings landing page
        return redirect(url_for('.email_preferences_view'))

    @expose('/password/', methods=('POST', 'GET'))
    def password_view(self):
        if request.method == 'POST':
            user = login.current_user
            if user.password == generate_password_hash(request.form['current_password'], user.salt):
                if request.form['new_password'] == request.form['repeat_password']:
                    salt = generate_random_salt()
                    user.password = generate_password_hash(request.form['new_password'], salt)
                    user.salt = salt
                    save_to_db(user, "password changed")
                    flash('Password changed successfully.', 'success')
                else:
                    flash('The new password and the repeat don\'t match.', 'danger')
            else:
                flash('The current password is incorrect.', 'danger')

        return self.render('/gentelella/admin/settings/pages/password.html')

    @expose('/email-preferences/')
    def email_preferences_view(self):
        events = DataGetter.get_all_events()
        message_settings = DataGetter.get_all_message_setting()
        settings = DataGetter.get_email_notification_settings(login.current_user.id)
        return self.render('/gentelella/admin/settings/pages/email_preferences.html',
                           settings=settings, events=events, message_settings=message_settings)

    @expose('/email/toggle/', methods=('POST',))
    def email_toggle_view(self):
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
