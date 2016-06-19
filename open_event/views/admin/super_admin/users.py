from flask import request, url_for, redirect
from flask_admin import expose
from flask.ext import login
from ....helpers.data_getter import DataGetter
from flask_admin import BaseView


class SuperAdminUsersView(BaseView):
    def is_accessible(self):
        return login.current_user.is_authenticated

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('admin.login_view', next=request.url))

    @expose('/')
    def index_view(self):
        user_list = []
        users = DataGetter.get_all_users()
        for user in users:
            event_roles = DataGetter.get_event_roles_for_user(user.id)
            user_list.append({
                'user': user,
                'event_roles': event_roles,}
            )
        return self.render('/gentelella/admin/super_admin/users/users.html', user_list=user_list)
