from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema, Relationship

from app.api.helpers.utilities import dasherize


class CustomSystemRoleSchema(Schema):
    """
    Api schema for Custom System Role Model
    """
    class Meta:
        """
        Meta class for Custom System Role Api Schema
        """
        type_ = 'custom-system-role'
        self_view = 'v1.custom_system_role_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    panel_permissions = Relationship(attribute='panel_permissions',
                          self_view='v1.custom_system_roles_panel_permissions',
                          self_view_kwargs={'id': '<id>'},
                          related_view='v1.panel_permission_list',
                          related_view_kwargs={'custom_system_role_id': '<id>'},
                          schema='PanelPermissionSchema',
                          many=True,
                          type_='panel-permission')
