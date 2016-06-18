from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from flask import request, url_for, redirect
from ....helpers.data import DataManager
from ....helpers.data_getter import DataGetter
from ....helpers import helpers as Helper


class InviteView(ModelView):

    @expose('/create/', methods=('GET', 'POST'))
    def create_view(self, event_id):
        if request.method == 'POST':
            email = request.form['email']
            user = DataGetter.get_user_by_email(email)
            event = DataGetter.get_event(event_id)
            if user:
                DataManager.add_invite_to_event(user.id, event_id)
                hash = DataGetter.get_invite_by_user_id(user.id).hash
                link = url_for('session.new_view', event_id=event_id, user_id=user.id, hash=hash, _external=True)
                Helper.send_email_invitation(email, event.name, link)

        return redirect(url_for('event.details_view', event_id=event_id))
