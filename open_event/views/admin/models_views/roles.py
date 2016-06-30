from flask.ext.admin import BaseView
from flask_admin import expose
from flask import request, url_for, redirect, flash
from ....helpers.data import DataManager
from ....helpers.data_getter import DataGetter
from open_event.helpers.permission_decorators import is_organizer
from open_event.helpers import helpers as Helper
from open_event.helpers.system_notifications import EVENT_ROLE_INVITE


class RoleView(BaseView):
    @expose('/', methods=('GET', 'POST'))
    def index_view(self, event_id):
        return ''

    @expose('/new/', methods=('POST',))
    @is_organizer
    def create_view(self, event_id):
        if request.method == 'POST':
            email = request.form.get('user_email')
            role_name = request.form.get('user_role')

            event = DataGetter.get_event(event_id)
            role = DataGetter.get_role_by_name(role_name)

            user = DataGetter.get_user_by_email(email)

            invite_link = DataManager.add_event_role_invite(email, role_name, event_id)

            if not user:
                # Send an email with the signup-invitation link
                signup_invite_link = url_for('admin.register_view',
                                             next=invite_link,
                                             _external=True)
                Helper.send_email_for_event_role_invite(email,
                                                        role.title_name,
                                                        event.name,
                                                        signup_invite_link)
                print signup_invite_link

                flash('An email invitation has been sent to user')
            else:
                # Send a notification with the invitation link

                title = EVENT_ROLE_INVITE['title'].format(
                    role=role.title_name,
                    event=event.name
                )
                message = EVENT_ROLE_INVITE['message'].format(
                    email=email,
                    role=role.title_name,
                    event=event.name,
                    link=invite_link
                )

                DataManager.create_user_notification(user=user,
                                                     title=title,
                                                     message=message)

                flash('A notification has been sent to user')

        return redirect(url_for('events.details_view', event_id=event_id))

    @expose('/<int:uer_id>/delete/', methods=('GET',))
    @is_organizer
    def delete_view(self, event_id, uer_id):
        DataManager.remove_role(uer_id)
        return redirect(url_for('events.details_view', event_id=event_id))

    @expose('/<int:uer_id>/update/', methods=('POST',))
    @is_organizer
    def edit_view(self, event_id, uer_id):
        uer = DataGetter.get_user_event_role(uer_id)
        DataManager.update_user_event_role(request.form, uer)
        return redirect(url_for('events.details_view', event_id=event_id))

