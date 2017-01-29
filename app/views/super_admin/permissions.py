from flask import Blueprint
from flask import render_template
from flask import request, redirect, url_for, flash

from app.helpers.data import DataManager
from app.helpers.data_getter import DataGetter
from app.models.system_role import CustomSysRole
from app.models.user import SYS_ROLES_LIST
from app.views.super_admin import PERMISSIONS, check_accessible, PANEL_LIST, list_navbar

sadmin_permissions = Blueprint('sadmin_permissions', __name__, url_prefix='/admin/permissions')


@sadmin_permissions.before_request
def verify_accessible():
    return check_accessible(PERMISSIONS)


@sadmin_permissions.route('/')
def index_view():
    # System-Role (Panel) Permissions
    builtin_sys_perms = dict()
    for role in SYS_ROLES_LIST:
        builtin_sys_perms[role] = dict()
        for panel in PANEL_LIST:
            builtin_sys_perms[role][panel] = True

    custom_sys_perms = dict()
    custom_sys_roles = DataGetter.get_custom_sys_roles()
    get_panel_perm = DataGetter.get_panel_permission
    for role in custom_sys_roles:
        custom_sys_perms[role] = dict()
        for panel in PANEL_LIST:
            perm = get_panel_perm(role, panel)
            custom_sys_perms[role][panel] = False if not perm else perm.can_access

    # User Permissions
    user_perms = DataGetter.get_user_permissions()

    # Event-Role Permissions
    event_perms = dict()
    roles = DataGetter.get_roles()
    services = DataGetter.get_services()
    get_permission = DataGetter.get_permission_by_role_service

    for role in roles:
        event_perms[role] = dict()
        for service in services:
            event_perms[role][service.name] = dict()
            p = get_permission(role=role, service=service)

            event_perms[role][service.name]['c'] = False if not p else p.can_create
            event_perms[role][service.name]['r'] = False if not p else p.can_read
            event_perms[role][service.name]['u'] = False if not p else p.can_update
            event_perms[role][service.name]['d'] = False if not p else p.can_delete

    return render_template(
        'gentelella/super_admin/permissions/permissions.html',
        event_perms=sorted(event_perms.iteritems(),
                           key=lambda (k, v): k.name),
        custom_sys_perms=custom_sys_perms,
        builtin_sys_perms=builtin_sys_perms,
        user_perms=user_perms,
        panel_list=PANEL_LIST,
        navigation_bar=list_navbar())


@sadmin_permissions.route('/event-roles/', methods=('POST',))
def event_roles_view():
    if request.method == 'POST':
        DataManager.update_permissions(request.form)
    return redirect(url_for('.index_view'))


@sadmin_permissions.route('/system-roles/new/', methods=('POST', 'GET'))
def create_custom_sys_role():
    if request.method == 'POST':
        role_name = request.form.get('role_name')
        sys_role = CustomSysRole.query.filter_by(name=role_name).first()
        if sys_role:
            flash('A System Role with similar name already exists. Please choose a different name.')
            return redirect(url_for('.index_view'))
        DataManager.create_custom_sys_role(request.form)
    return redirect(url_for('.index_view'))


@sadmin_permissions.route('/system-roles/', methods=('POST', 'GET'))
def update_custom_sys_role():
    if request.method == 'POST':
        role_name = request.form.get('role_name')
        sys_role = CustomSysRole.query.filter_by(name=role_name).first()
        if not sys_role:
            flash('No such role exists.')
            return redirect(url_for('.index_view'))
        DataManager.update_custom_sys_role(request.form)
    return redirect(url_for('.index_view'))


@sadmin_permissions.route('/system-roles/delete/<int:role_id>/', methods=('POST', 'GET'))
def delete_custom_sys_role(role_id):
    DataManager.delete_custom_sys_role(role_id)
    return redirect(url_for('.index_view'))


@sadmin_permissions.route('/user-roles/', methods=('POST', 'GET'))
def user_roles_view():
    if request.method == 'POST':
        DataManager.update_user_permissions(request.form)
    return redirect(url_for('.index_view'))
