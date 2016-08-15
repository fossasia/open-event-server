from flask import request
from flask_admin import expose

from app.views.admin.super_admin.super_admin_base import SuperAdminBaseView, USERS
from ....helpers.data_getter import DataGetter
from ....helpers.data import update_role_to_admin, delete_from_db
from flask import url_for, redirect, flash
from app.helpers.data import trash_user, restore_user
from sqlalchemy_continuum import transaction_class
from app.models.event import Event


class SuperAdminUsersView(SuperAdminBaseView):
    PANEL_NAME = USERS

    @expose('/')
    def index_view(self):
        active_user_list = []
        trash_user_list = []
        all_user_list = []
        active_users = DataGetter.get_active_users()
        trash_users = DataGetter.get_trash_users()
        all_users = DataGetter.get_all_users()
        for user in all_users:
            event_roles = DataGetter.get_event_roles_for_user(user.id)
            all_user_list.append({
                'user': user,
                'event_roles': event_roles}
            )
        for user in active_users:
            event_roles = DataGetter.get_event_roles_for_user(user.id)
            active_user_list.append({
                'user': user,
                'event_roles': event_roles,}
            )
        for user in trash_users:
            event_roles = DataGetter.get_event_roles_for_user(user.id)
            trash_user_list.append({
                'user': user,
                'event_roles': event_roles,}
            )
        return self.render('/gentelella/admin/super_admin/users/users.html', active_user_list=active_user_list, trash_user_list=trash_user_list, all_user_list=all_user_list)

    @expose('/<user_id>/edit/', methods=('GET', 'POST'))
    def edit_view(self, user_id):
        update_role_to_admin(request.form, user_id)
        active_user_list = []
        trash_user_list = []
        active_users = DataGetter.get_active_users()
        trash_users = DataGetter.get_trash_users()
        for user in active_users:
            event_roles = DataGetter.get_event_roles_for_user(user.id)
            active_user_list.append({
                'user': user,
                'event_roles': event_roles,}
            )
        for user in trash_users:
            event_roles = DataGetter.get_event_roles_for_user(user.id)
            trash_user_list.append({
                'user': user,
                'event_roles': event_roles,}
            )
        return self.render('/gentelella/admin/super_admin/users/users.html', active_user_list=active_user_list, trash_user_list=trash_user_list)

    @expose('/<user_id>/', methods=('GET', 'POST'))
    def details_view(self, user_id):
        profile = DataGetter.get_user(user_id)
        return self.render('/gentelella/admin/profile/index.html',
                           profile=profile, user_id=user_id)


    @expose('/<user_id>/trash/', methods=('GET',))
    def trash_view(self, user_id):
        trash_user(user_id)
        flash("User" + user_id + " has been deleted.", "danger")
        return redirect(url_for('.index_view'))

    @expose('/<user_id>/restore/', methods=('GET',))
    def restore_view(self, user_id):
        restore_user(user_id)
        flash("User" + user_id + " has been restored.", "success")
        return redirect(url_for('.index_view'))

    @expose('/<user_id>/delete/', methods=('GET',))
    def delete_view(self, user_id):
        profile = DataGetter.get_user(user_id)
        if request.method == "GET":
            transaction = transaction_class(Event)
            transaction.query.filter_by(user_id=user_id).delete()
            delete_from_db(profile, "User's been permanently removed")
        flash("User" + user_id + " has been permenently deleted.", "danger")
        return redirect(url_for('.index_view'))
