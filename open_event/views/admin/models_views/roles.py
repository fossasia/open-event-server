from flask.ext.admin import BaseView
from flask_admin import expose
from flask import request, url_for, redirect
from ....helpers.data import DataManager
from ....helpers.data_getter import DataGetter
from open_event.helpers.permission_decorators import is_organizer

class RoleView(BaseView):
    @expose('/', methods=('GET', 'POST'))
    def index_view(self, event_id):
        return ''

    @expose('/new/', methods=('POST',))
    @is_organizer
    def create_view(self, event_id):
        DataManager.add_role_to_event(request.form, event_id)
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

