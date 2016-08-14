from flask import request
from flask_admin import expose

from app.views.admin.super_admin.super_admin_base import SuperAdminBaseView, PERMISSIONS
from app.helpers.data_getter import DataGetter
from app.helpers.data import DataManager


class SuperAdminPermissionsView(SuperAdminBaseView):
    PANEL_NAME = PERMISSIONS

    @expose('/', methods=('GET', 'POST'))
    def index_view(self):
        if request.method == 'POST':
            DataManager.update_permissions(request.form)

        perms = dict()
        roles = DataGetter.get_roles()
        services = DataGetter.get_services()
        get_permission = DataGetter.get_permission_by_role_service

        for role in roles:
            perms[role] = dict()
            for service in services:
                perms[role][service.name] = dict()
                p = get_permission(role=role, service=service)
                if not p:
                    perms[role][service.name]['c'] = False
                    perms[role][service.name]['r'] = False
                    perms[role][service.name]['u'] = False
                    perms[role][service.name]['d'] = False
                else:
                    perms[role][service.name]['c'] = p.can_create
                    perms[role][service.name]['r'] = p.can_read
                    perms[role][service.name]['u'] = p.can_update
                    perms[role][service.name]['d'] = p.can_delete

        return self.render(
            '/gentelella/admin/super_admin/permissions/permissions.html',
            perms=sorted(perms.iteritems(),
                         key=lambda (k, v): k.name))
