from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

from app.api.helpers.utilities import dasherize
from utils.common import use_defaults


@use_defaults()
class EventsRolePermissionSchema(Schema):
    """
    API Schema for Permission Model
    """

    class Meta:
        """
        Meta class for Notification API schema
        """

        type_ = 'event-role-permissions'
        self_view = 'v1.events_role_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'v1.events_role_list'
        inflect = dasherize

    id = fields.Str()
    can_create = fields.Boolean(default=False)
    can_read = fields.Boolean(default=False)
    can_update = fields.Boolean(default=False)
    can_delete = fields.Boolean(default=False)
    role = Relationship(
        self_view='v1.event_role_role',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.role_detail',
        related_view_kwargs={'id': '<role_id>'},
        schema='RoleSchema',
        type_='role',
    )
    service = Relationship(
        self_view='v1.event_role_service',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.service_detail',
        related_view_kwargs={'id': '<service_id>'},
        schema='ServiceSchema',
        type_='service',
    )
