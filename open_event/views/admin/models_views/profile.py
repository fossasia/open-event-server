from flask import request, url_for, redirect
from flask.ext.admin import BaseView
from flask_admin import expose
from flask.ext import login

from ....helpers.data import DataManager
from ....helpers.data_getter import DataGetter
from open_event.helpers.storage import upload


class ProfileView(BaseView):

    def is_accessible(self):
        return login.current_user.is_authenticated

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('admin.login_view', next=request.url))

    @expose('/')
    def index_view(self):
        profile = DataGetter.get_user(login.current_user.id)
        return self.render('/gentelella/admin/profile/index.html',
                           profile=profile)

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        if request.method == 'POST':
            avatar_img = request.files['avatar']
            url = upload(avatar_img, 'users/%d/avatar' % login.current_user.id)
            profile = DataManager.update_user(request.form, login.current_user.id, url)
            return redirect(url_for('.index_view'))
        profile = DataGetter.get_user(login.current_user.id)
        return self.render('/gentelella/admin/profile/edit.html', profile=profile)
