from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from flask import request, url_for, redirect
from ....helpers.data import DataManager
from ....helpers.data_getter import DataGetter


class SessionView(ModelView):

    @expose('/new/<user_id>/<hash>/', methods=('GET', 'POST'))
    def create_view(self, event_id, user_id, hash):
        invite = DataGetter.get_invite_by_user_id(user_id)
        if invite and invite.hash == hash:
            if request.method == 'POST':
                DataManager.add_session_to_event(request.form, event_id)
                return redirect(url_for('event.details_view', event_id=event_id))
            return self.render('/gentelella/admin/session/new.html')
