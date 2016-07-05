import unicodedata
from flask import request, url_for, redirect, jsonify
from flask.ext.admin import BaseView
from flask_admin import expose
from flask.ext import login

from open_event.helpers.data import DataManager, save_to_db
from open_event.models.email_notifications import EmailNotification
from ....helpers.data_getter import DataGetter


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

    @expose('/email-preferences')
    def email_preferences_view(self):
        events = DataGetter.get_all_events()
        settings = DataGetter.get_email_notification_settings(login.current_user.id)
        return self.render('/gentelella/admin/settings/pages/email_preferences.html',
                           settings=settings, events=events)

    @expose('/email/toggle', methods=('POST',))
    def email_toggle_view(self):
        if request.method == 'POST':
            name = request.form.get('name')
            value = int(request.form.get('value'))
            event_id = request.form.get('event_id')

            message = ''
            if name == 'global_email':
                email_notifications = EmailNotification.query.filter_by(user_id=login.current_user.id).all()
                for email_notification in email_notifications:
                    email_notification.next_event = value
                    email_notification.new_paper = value
                    email_notification.session_schedule = value
                    email_notification.session_accept_reject = value
                    save_to_db(email_notification, "EmailSettings Toggled")
            else:
                name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore')
                email_notification = DataGetter\
                    .get_email_notification_settings_by_event_id(login.current_user.id, event_id)
                setattr(email_notification, name, value)
                save_to_db(email_notification, "EmailSettings Toggled")

            return jsonify({
                'status': 'ok',
                'message': message
            })
