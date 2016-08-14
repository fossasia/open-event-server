from flask import request, redirect, url_for
from flask_admin import expose

from app.views.admin.super_admin.super_admin_base import SuperAdminBaseView, PERMISSIONS, PANEL_LIST
from app.models.user import SUPERADMIN, ADMIN
from app.helpers.data_getter import DataGetter
from app.helpers.data import DataManager


class SuperAdminPermissionsView(SuperAdminBaseView):
    PANEL_NAME = PERMISSIONS

    @expose('/', methods=('GET',))
    def index_view(self):
        # System-Role (Panel) Permissions
        sys_perms = dict()
        sys_perms[SUPERADMIN] = dict()
        sys_perms[ADMIN] = dict()
        get_panel_perm = DataGetter.get_panel_permission

        for panel in PANEL_LIST:
            p = get_panel_perm(role_name=SUPERADMIN, panel_name=panel)
            sys_perms[SUPERADMIN][panel] = False if not p else p.can_access

            p = get_panel_perm(role_name=ADMIN, panel_name=panel)
            sys_perms[ADMIN][panel] = False if not p else p.can_access

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
            sys_perms=sys_perms)

    @expose('/event-roles', methods=('POST','GET'))
    def event_roles_view(self):
        if request.method == 'POST':
            DataManager.update_permissions(request.form)
        return redirect(url_for('.index_view'))

    @expose('/system-roles', methods=('POST','GET'))
    def system_roles_view(self):
        if request.method == 'POST':
            DataManager.update_panel_permissions(request.form)
        return redirect(url_for('.index_view'))
