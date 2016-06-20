from flask_admin import expose

from open_event.views.admin.super_admin.super_admin_base import SuperAdminBaseView
from open_event.helpers.data_getter import DataGetter


class SuperAdminPermissionsView(SuperAdminBaseView):
    @expose('/')
    def index_view(self):
        perms = dict()
        roles = DataGetter.get_roles()
        services = DataGetter.get_services()
        get_permissions = DataGetter.get_permissions_by_role_service

        for role in roles:
            perms[role] = dict()
            for service in services:
                perms[role][service.name] = dict()
                gp = list(get_permissions(role=role, service=service))
                if not gp:
                    perms[role][service.name]['c'] = False
                    perms[role][service.name]['r'] = False
                    perms[role][service.name]['u'] = False
                    perms[role][service.name]['d'] = False
                else:
                    for p in gp:
                        perms[role][service.name]['c'] = p.can_create
                        perms[role][service.name]['r'] = p.can_read
                        perms[role][service.name]['u'] = p.can_update
                        perms[role][service.name]['d'] = p.can_delete

        return self.render(
            '/gentelella/admin/super_admin/permissions/permissions.html',
            perms=sorted(perms.iteritems(), key=lambda (k, v): k.name))
