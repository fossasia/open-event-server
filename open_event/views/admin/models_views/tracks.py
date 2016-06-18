from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from flask import request, url_for, redirect
from ....helpers.data import DataManager
from open_event.helpers.permission_decorators import *

class TracksView(ModelView):

    @expose('/create/', methods=('GET', 'POST'))
    @can_access
    def create_view(self, event_id):
        if request.method == 'POST':
            print request.form
            DataManager.create_new_track(request.form, event_id)
        return redirect(url_for('event.details_view', event_id=event_id))
