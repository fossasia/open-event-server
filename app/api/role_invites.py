from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from datetime import datetime
from pytz import timezone

from app.api.helpers.utilities import dasherize
from app.models import db
from app.models.role import Role
from app.models.event import Event
from app.models.role_invite import RoleInvite
from app.api.bootstrap import api
from app.api.helpers.permissions import jwt_required
from app.api.helpers.db import safe_query


class RoleInviteSchema(Schema):
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

    id = fields.Str(dump_only=True)
    email = fields.Str()
    hash = fields.Str()
    created_at = fields.DateTime(dump_only=True, timezone=True)
    role_id = fields.Integer()
    is_declined = fields.Bool(default=False)
    event = Relationship(attribute='event',
                         self_view='v1.role_invite_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'role_invite_id': '<id>'},
                         schema='EventSchema',
                         type_='event')
    role = Relationship(attribute='role',
                        self_view='v1.role_invite_role',
                        self_view_kwargs={'id': '<id>'},
                        related_view='v1.role_detail',
                        related_view_kwargs={'role_invite_id': '<id>'},
                        schema='RoleSchema',
                        type_='role')


class RoleInviteList(ResourceList):
    """
    List and create role invites
    """

    def query(self, view_kwargs):
        """
        query method for role invites list
        :param view_kwargs:
        :return:
        """

        query_ = self.session.query(RoleInvite)
        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
            query_ = query_.filter_by(event_id=event.id)
        elif view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
            query_ = query_.join(Event).filter(Event.id == event.id)
        return query_

    def before_create_object(self, data, view_kwargs):
        """
        method to create object before post
        :param data:
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
            data['event_id'] = event.id

        elif view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
            data['event_id'] = event.id

    view_kwargs = True
    decorators = (api.has_permission('is_organizer', fetch='event_id', fetch_as="event_id", methods="POST",
                                     check=lambda a: a.get('event_id') or a.get('event_identifier')),)
    schema = RoleInviteSchema
    data_layer = {'session': db.session,
                  'model': RoleInvite,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object
                  }}


class RoleInviteDetail(ResourceDetail):
    """
    Role invite detail by id
    """

    decorators = (api.has_permission('is_coorganizer', methods="PATCH,DELETE", fetch="event_id", fetch_as="event_id",
                                     model=RoleInvite, check=lambda a: a.get('id') is not None),)
    schema = RoleInviteSchema
    data_layer = {'session': db.session,
                  'model': RoleInvite}


class RoleInviteRelationship(ResourceRelationship):
    """
    Role invite Relationship
    """
    decorators = (jwt_required,)
    schema = RoleInviteSchema
    data_layer = {'session': db.session,
                  'model': RoleInvite}
