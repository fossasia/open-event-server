from marshmallow import Schema as NormalSchema
from marshmallow import post_dump
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

from app.api.helpers.utilities import dasherize
from app.api.schema.event_invoices import EventInvoiceSchema
from app.api.schema.events import EventSchemaPublic
from app.api.schema.orders import OrderSchema
from app.api.schema.role_invites import RoleInviteSchema
from app.api.schema.roles import RoleSchema
from app.api.schema.sessions import SessionSchema


class NotificationActorSchema(NormalSchema):
    id = fields.Function(lambda o: o.actor.id)
    first_name = fields.Function(lambda o: o.actor.first_name)
    last_name = fields.Function(lambda o: o.actor.last_name)
    public_name = fields.Function(lambda o: o.actor.public_name)
    avatar_url = fields.Function(lambda o: o.actor.avatar_url)
    thumbnail_image_url = fields.Function(lambda o: o.actor.thumbnail_image_url)


def normalize_jsonapi_data(schema, obj):
    data, _ = schema.dump(obj)
    attribs = data['data']['attributes']
    attribs['id'] = data['data']['id']

    return attribs


class NotificationContentSchema(NormalSchema):
    type = fields.Str(dump_only=True)
    target_type = fields.Str(dump_only=True)
    target_id = fields.Int(dump_only=True)
    target_action = fields.Str(dump_only=True)
    actors = fields.Nested(NotificationActorSchema, many=True)

    @post_dump(pass_original=True)
    def add_target(self, data, obj):
        if obj.target is None:
            # handler -> if target data is deleted after generation of notification.
            # to be implemented in future -> delete notification if target is deleted ex. RoleInvite.
            return {}
        event = None
        if obj.target_type == 'Order':
            serialized = normalize_jsonapi_data(
                OrderSchema(only=('id', 'amount', 'identifier')), obj.target
            )
            data['order'] = serialized
            event = obj.target.event
        elif obj.target_type == 'Session':
            serialized = normalize_jsonapi_data(
                SessionSchema(only=('id', 'title')), obj.target
            )
            data['session'] = serialized
            event = obj.target.event
        elif obj.target_type == 'EventInvoice':
            serialized = normalize_jsonapi_data(
                EventInvoiceSchema(
                    only=('id', 'identifier', 'amount', 'issued_at', 'due_at', 'status')
                ),
                obj.target,
            )
            data['invoice'] = serialized
            event = obj.target.event
        elif obj.target_type == 'RoleInvite':
            serialized = normalize_jsonapi_data(RoleInviteSchema(), obj.target)
            data['event_invite'] = serialized
            data['role'] = normalize_jsonapi_data(RoleSchema(), obj.target.role)
            event = obj.target.event

        if event:
            data['event'] = normalize_jsonapi_data(
                EventSchemaPublic(only=('id', 'name', 'identifier')), obj.target.event
            )
        return data


class NotificationSchema(Schema):
    """
    API Schema for Notification Model
    """

    class Meta:
        """
        Meta class for Notification API schema
        """

        type_ = 'notification'
        self_view = 'v1.notification_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    is_read = fields.Boolean()
    content = fields.Nested(NotificationContentSchema)
    user = Relationship(
        self_view='v1.notification_user',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_detail',
        related_view_kwargs={'notification_id': '<id>'},
        schema='UserSchema',
        type_='user',
    )
