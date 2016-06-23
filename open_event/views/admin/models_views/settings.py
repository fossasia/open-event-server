from flask import request, url_for, redirect
from flask.ext.admin import BaseView
from flask_admin import expose
from flask.ext import login

from ....helpers.data import DataManager
from ....helpers.data_getter import DataGetter


class SettingsView(BaseView):

    def is_accessible(self):
        return login.current_user.is_authenticated

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('admin.login_view', next=request.url))

    @expose('/')
    def index_view(self):
        settings = DataGetter.get_settings(login.current_user.id)
        return self.render('/gentelella/admin/settings/index.html',
                           settings=settings)

    @expose('/edit/<user_id>', methods=('GET', 'POST'))
    def edit_view(self, user_id):
        if request.method == 'POST':
            settings = DataManager.update_settings(request.form, user_id)
            return redirect(url_for('.index_view'))
        settings = DataGetter.get_settings(int(user_id))
        return self.render('/gentelella/admin/settings/edit.html', settings=settings)
