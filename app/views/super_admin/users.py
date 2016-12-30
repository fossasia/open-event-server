from flask import Blueprint
from flask import request
from flask import url_for, redirect, flash, render_template
from flask.ext.login import current_user
from flask.ext.restplus import abort
from sqlalchemy_continuum import transaction_class

from app.helpers.data import delete_from_db, DataManager, save_to_db
from app.helpers.data import trash_user, restore_user
from app.helpers.data_getter import DataGetter
from app.models.event import Event
from app.views.super_admin import USERS, check_accessible, list_navbar

sadmin_users = Blueprint('sadmin_users', __name__, url_prefix='/admin/users')


@sadmin_users.before_request
def verify_accessible():
    return check_accessible(USERS)


@sadmin_users.route('/')
def index_view():
    active_user_list = []
    trash_user_list = []
    all_user_list = []
    active_users = DataGetter.get_active_users()
    trash_users = DataGetter.get_trash_users()
    all_users = DataGetter.get_all_users()
    custom_sys_roles = DataGetter.get_custom_sys_roles()
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
            'event_roles': event_roles, }
        )
    for user in trash_users:
        event_roles = DataGetter.get_event_roles_for_user(user.id)
        trash_user_list.append({
            'user': user,
            'event_roles': event_roles, }
        )
    return render_template('gentelella/admin/super_admin/users/users.html',
                           active_user_list=active_user_list,
                           trash_user_list=trash_user_list,
                           all_user_list=all_user_list,
                           custom_sys_roles=custom_sys_roles,
                           navigation_bar=list_navbar())


@sadmin_users.route('/<user_id>/edit/', methods=('GET', 'POST'))
def edit_view(user_id):
    return redirect(url_for('.index_view'))


@sadmin_users.route('/<user_id>/update-roles', methods=('GET', 'POST'))
def update_roles_view(user_id):
    if current_user.is_super_admin:
        user = DataGetter.get_user(user_id)
        user.is_admin = request.form.get('admin') == 'yes'
        save_to_db(user)

        custom_sys_roles = DataGetter.get_custom_sys_roles()
        for role in custom_sys_roles:
            field = request.form.get('custom_role-{}'.format(role.id))
            if field:
                DataManager.get_or_create_user_sys_role(user, role)
            else:
                DataManager.delete_user_sys_role(user, role)

        return redirect(url_for('.index_view'))
    else:
        abort(403)


@sadmin_users.route('/<user_id>/', methods=('GET', 'POST'))
def details_view(user_id):
    profile = DataGetter.get_user(user_id)
    return render_template('gentelella/admin/profile/index.html',
                           profile=profile, user_id=user_id)


@sadmin_users.route('/<user_id>/trash/', methods=('GET',))
def trash_view(user_id):
    profile = DataGetter.get_user(user_id)
    if profile.is_super_admin:
        abort(403)
    trash_user(user_id)
    flash("User" + user_id + " has been deleted.", "danger")
    return redirect(url_for('.index_view'))


@sadmin_users.route('/<user_id>/restore/', methods=('GET',))
def restore_view(user_id):
    restore_user(user_id)
    flash("User" + user_id + " has been restored.", "success")
    return redirect(url_for('.index_view'))


@sadmin_users.route('/<user_id>/delete/', methods=('GET',))
def delete_view(user_id):
    profile = DataGetter.get_user(user_id)
    if profile.is_super_admin:
        abort(403)
    if request.method == "GET":
        transaction = transaction_class(Event)
        transaction.query.filter_by(user_id=user_id).delete()
        delete_from_db(profile, "User's been permanently removed")
    flash("User" + user_id + " has been permanently deleted.", "danger")
    return redirect(url_for('.index_view'))
