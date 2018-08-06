from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema, Relationship

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
    role_id = fields.Integer(allow_none=False)
    can_access = fields.Boolean()
    role = Relationship(attribute='role',
                        self_view='v1.panel_permission_role',
                        self_view_kwargs={'id': '<id>'},
                        related_view='v1.custom_system_role_detail',
                        related_view_kwargs={'role_id': '<id>'},
                        schema='CustomSystemRoleSchema',
                        type_='custom-system-role')
