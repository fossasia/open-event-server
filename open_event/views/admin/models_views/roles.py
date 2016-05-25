from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from flask import request, url_for, redirect
from ....helpers.data import DataManager

class RoleView(ModelView):

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self, event_id):
        if request.method == 'POST':
            DataManager.add_role_to_event(request.form, event_id)
        return redirect(url_for('event.details_view', event_id=event_id))

