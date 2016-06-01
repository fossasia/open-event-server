from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from flask import request, url_for, redirect
from ....helpers.data import DataManager
from ....helpers.data_getter import DataGetter
from ....helpers import helpers as Helper


class InviteView(ModelView):

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self, event_id):
        if request.method == 'POST':
            email = request.form['email']
            user = DataGetter.get_user_by_email(email)
            event = DataGetter.get_event(event_id)
            if user:
                DataManager.add_invite_to_event(user.id, event_id)
                Helper.send_email_invitation(email, user.login, event.name)

        return redirect(url_for('event.details_view', event_id=event_id))
