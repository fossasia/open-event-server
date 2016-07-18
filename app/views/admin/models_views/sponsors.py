from flask.ext.admin import BaseView
from flask_admin import expose
from ....helpers.data_getter import DataGetter
from app.helpers.permission_decorators import *
from app.helpers.data import delete_from_db

class SponsorsView(BaseView):
    @expose('/', methods=('GET', 'POST'))
    def index_view(self, event_id):
        return ''

    @expose('/new/', methods=('GET', 'POST'))
    @can_access
    def create_view(self, event_id):
        event = DataGetter.get_event(event_id)
        return self.render('/gentelella/admin/event/sponsors/new.html', event_id=event_id, event=event)

    @expose('/<sponsor_id>/delete/', methods=('GET', ))
    @can_access
    def delete_view(self, event_id, sponsor_id):
        sponsor = DataGetter.get_sponsor(sponsor_id)
        delete_from_db(sponsor, "Sponsor deleted")
        return redirect(url_for('events.details_view', event_id=event_id))

    @expose('/<sponsor_id>/edit/', methods=('POST', 'GET'))
    @can_access
    def edit_view(self, event_id, sponsor_id):
        event = DataGetter.get_event(event_id)
        return self.render('/gentelella/admin/event/sponsors/edit.html', event_id=event_id, event=event)
