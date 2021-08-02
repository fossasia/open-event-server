from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

from app.api.helpers.utilities import dasherize


class PanelPermissionSchema(Schema):
    """
    API Schema for panel permission Model
    """

    class Meta:
        """
        Meta class for user email API schema
        """

        type_ = 'panel-permission'
        self_view = 'v1.panel_permission_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    panel_name = fields.String(allow_none=False)
    can_access = fields.Boolean()
    custom_system_roles = Relationship(
        many=True,
        self_view='v1.panel_permissions_custom_system_roles',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.custom_system_role_list',
        related_view_kwargs={'panel_id': '<id>'},
        schema='CustomSystemRoleSchema',
        type_='custom-system-role',
    )
