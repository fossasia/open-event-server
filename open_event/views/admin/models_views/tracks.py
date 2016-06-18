from flask.ext.admin import BaseView
from flask.ext.restplus import abort
from flask_admin import expose
from flask import request, url_for, redirect
from ....helpers.data import DataManager
from open_event.helpers.permission_decorators import *

class TracksView(BaseView):

    @expose('/')
    def index_view(self):
        abort(404)

    @expose('/create/', methods=('GET', 'POST'))
    @can_access
    def create_view(self, event_id):
        if request.method == 'POST':
            print request.form
            DataManager.create_new_track(request.form, event_id)
        return redirect(url_for('events.details_view', event_id=event_id))
