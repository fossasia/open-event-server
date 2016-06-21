from flask.ext.admin import BaseView
from flask_admin import expose
from flask import request, url_for, redirect
from ....helpers.data import DataManager
from ....helpers.data_getter import DataGetter
from open_event.helpers.permission_decorators import *

class RoleView(BaseView):
    @expose('/', methods=('GET', 'POST'))
    def index_view(self, event_id):
        return ''

    @expose('/new/', methods=('GET', 'POST'))
    @is_organizer
    def create_view(self, event_id):
        if request.method == 'POST':
            DataManager.add_role_to_event(request.form, event_id)
        return redirect(url_for('events.details_view', event_id=event_id))

    @expose('/<uer_id>/delete/', methods=('GET',))
    @is_organizer
    def delete_view(self, event_id, uer_id):
        if request.method == "GET":
            DataManager.remove_role(uer_id)
        return redirect(url_for('events.details_view', event_id=event_id))

    @expose('/<uer_id>/update/', methods=('POST',))
    @is_organizer
    def edit_view(self, event_id, uer_id):
        if request.method == "POST":
            uer = DataGetter.get_user_event_role(uer_id)
            DataManager.update_user_event_role(request.form, uer)
        return redirect(url_for('events.details_view', event_id=event_id))

