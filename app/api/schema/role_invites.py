from flask_rest_jsonapi.exceptions import ObjectNotFound
from marshmallow import validates_schema, validate
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship
from sqlalchemy.orm.exc import NoResultFound

from app.api.helpers.exceptions import UnprocessableEntity
from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema
from app.models.role import Role
from app.models.role_invite import RoleInvite
from utils.common import use_defaults


@use_defaults()
class RoleInviteSchema(SoftDeletionSchema):
    """
    Api Schema for role invite model
    """

    class Meta:
        """
        Meta class for role invite Api Schema
        """
        type_ = 'role-invite'
        self_view = 'v1.role_invite_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    @validates_schema(pass_original=True)
    def validate_satus(self, data, original_data):
        if 'role' in data and 'role_name' in data:
            try:
                role = Role.query.filter_by(id=data['role']).one()
            except NoResultFound:
                raise ObjectNotFound({'source': '/data/role'}, "Role not found")
            if role.name != data['role_name']:
                raise UnprocessableEntity({'pointer': '/data/attributes/role'},
                                          "Role id do not match role name")
        if 'id' in original_data['data']:
            try:
                role_invite = RoleInvite.query.filter_by(id=original_data['data']['id']).one()
            except NoResultFound:
                raise ObjectNotFound({'source': '/data/id'}, "Role invite not found")
            if 'role' not in data:
                data['role'] = role_invite.role.id
            if 'role_name' in data:
                try:
                    role = Role.query.filter_by(id=data['role']).one()
                except NoResultFound:
                    raise ObjectNotFound({'source': '/data/role'}, "Role not found")
                if role.name != data['role_name']:
                    raise UnprocessableEntity({'pointer': '/data/attributes/role'},
                                              "Role id do not match role name")

    id = fields.Str(dump_only=True)
    email = fields.Str(required=True)
    hash = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True, timezone=True)
    role_name = fields.Str(validate=validate.OneOf(choices=["organizer", "coorganizer", "track_organizer",
                           "moderator", "attendee", "registrar"]))
    status = fields.Str(validate=validate.OneOf(choices=["pending", "accepted", "declined"]),
                        default="pending")
    event = Relationship(attribute='event',
                         self_view='v1.role_invite_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'role_invite_id': '<id>'},
                         schema='EventSchemaPublic',
                         type_='event')
    role = Relationship(attribute='role',
                        self_view='v1.role_invite_role',
                        self_view_kwargs={'id': '<id>'},
                        related_view='v1.role_detail',
                        related_view_kwargs={'role_invite_id': '<id>'},
                        schema='RoleSchema',
                        type_='role')
