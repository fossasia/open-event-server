from flask.ext.admin import BaseView
from flask.ext.restplus import abort
from flask_admin import expose
from flask import request, url_for, redirect
from ....helpers.data import DataManager
from ....helpers.data_getter import DataGetter
from ....helpers import helpers as Helper


class InviteView(BaseView):

    @expose('/')
    def index_view(self):
        abort(404)

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self, event_id):
        if request.method == 'POST':
            email = request.form['email']
            user = DataGetter.get_user_by_email(email)
            event = DataGetter.get_event(event_id)
            if user:
                DataManager.add_invite_to_event(user.id, event_id)
                hash = DataGetter.get_invite_by_user_id(user.id).hash
                link = url_for('event_sessions.new_view', event_id=event_id, user_id=user.id, hash=hash, _external=True)
                Helper.send_email_invitation(email, event.name, link)
                cfs_link = url_for('event_detail.display_event_cfs', identifier=event.identifier)
                Helper.send_notif_invite_papers(user, event.name, cfs_link, link)

        return redirect(url_for('events.details_view', event_id=event_id))
