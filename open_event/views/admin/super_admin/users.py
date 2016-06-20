from flask import request
from flask_admin import expose

from open_event.views.admin.super_admin.super_admin_base import SuperAdminBaseView
from ....helpers.data_getter import DataGetter
from ....helpers.data import update_role_to_admin, delete_from_db
from flask import request, url_for, redirect, flash


class SuperAdminUsersView(SuperAdminBaseView):
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

    @expose('/<user_id>/edit/', methods=('GET', 'POST'))
    def edit_view(self, user_id):
        update_role_to_admin(request.form, user_id)
        user_list = []
        users = DataGetter.get_all_users()
        for user in users:
            event_roles = DataGetter.get_event_roles_for_user(user.id)
            user_list.append({
                'user': user,
                'event_roles': event_roles,}
            )
        return self.render('/gentelella/admin/super_admin/users/users.html', user_list=user_list)

    @expose('/<user_id>/', methods=('GET', 'POST'))
    def details_view(self, user_id):
        profile = DataGetter.get_user(user_id)
        return self.render('/gentelella/admin/profile/index.html',
                           profile=profile, user_id=user_id)

    @expose('/<user_id>/delete/', methods=('GET',))
    def delete_view(self, user_id):
        profile = DataGetter.get_user(user_id)
        if request.method == "GET":
            delete_from_db(profile, "User's been removed")
        flash("User" + user_id + " has been deleted.", "danger")
        return redirect(url_for('.index_view'))
