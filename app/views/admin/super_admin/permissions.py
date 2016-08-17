from flask import request, redirect, url_for
from flask_admin import expose

from app.views.admin.super_admin.super_admin_base import SuperAdminBaseView, PERMISSIONS, PANEL_LIST
from app.models.user import SYS_ROLES_LIST
from app.helpers.data_getter import DataGetter
from app.helpers.data import DataManager


class SuperAdminPermissionsView(SuperAdminBaseView):
    PANEL_NAME = PERMISSIONS

    @expose('/', methods=('GET',))
    def index_view(self):
        # System-Role (Panel) Permissions
        sys_perms = dict()
        get_panel_perm = DataGetter.get_panel_permission

        for sys_role in SYS_ROLES_LIST:
            sys_perms[sys_role] = dict()
            for panel in PANEL_LIST:
                p = get_panel_perm(role_name=sys_role, panel_name=panel)
                sys_perms[sys_role][panel] = False if not p else p.can_access

        ## User Permissions
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

        return self.render(
            '/gentelella/admin/super_admin/permissions/permissions.html',
            event_perms=sorted(event_perms.iteritems(),
                         key=lambda (k, v): k.name),
            sys_perms=sys_perms, user_perms=user_perms)

    @expose('/event-roles', methods=('POST','GET'))
    def event_roles_view(self):
        if request.method == 'POST':
            DataManager.update_permissions(request.form)
        return redirect(url_for('.index_view'))

    @expose('/system-roles', methods=('POST', 'GET'))
    def system_roles_view(self):
        if request.method == 'POST':
            DataManager.update_panel_permissions(request.form)
        return redirect(url_for('.index_view'))

    @expose('/user-roles', methods=('POST', 'GET'))
    def user_roles_view(self):
        if request.method == 'POST':
            DataManager.update_user_permissions(request.form)
        return redirect(url_for('.index_view'))
