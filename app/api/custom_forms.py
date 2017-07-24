from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields

from app.api.bootstrap import api
from app.api.helpers.utilities import dasherize
from app.api.helpers.permissions import jwt_required
from app.models import db
from app.models.custom_form import CustomForms
from app.models.event import Event
from app.api.helpers.db import safe_query
import marshmallow.validate as validate
from app.api.helpers.utilities import require_relationship


class CustomFormSchema(Schema):
    """
    API Schema for Custom Forms database model
    """
    class Meta:
        """
        Meta class for CustomForm Schema
        """
        type_ = 'custom_form'
        self_view = 'v1.custom_form_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Integer(dump_only=True)
    field_identifier = fields.Str(required=True)
    form = fields.Str(required=True)
    type = fields.Str(default="text", validate=validate.OneOf(
        choices=["text", "checkbox", "select", "file", "image"]))
    is_required = fields.Boolean(default=False)
    is_included = fields.Boolean(default=False)
    is_fixed = fields.Boolean(default=False)
    event = Relationship(attribute='event',
                         self_view='v1.custom_form_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'custom_form_id': '<id>'},
                         schema='EventSchema',
                         type_='event')


class CustomFormList(ResourceList):
    """
    Create and List Custom Forms
    """

    def before_post(self, args, kwargs, data):
        """
        method to check for required relationship with event
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['event'], data)

    def query(self, view_kwargs):
        """
        query method for different view_kwargs
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(CustomForms)
        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
            query_ = query_.join(Event).filter(Event.id == event.id)
        elif view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
            query_ = query_.join(Event).filter(Event.id == event.id)
        return query_

    def before_create_object(self, data, view_kwargs):
        """
        before create method for object
        :param data:
        :param view_kwargs:
        :return:
        """
        event = None
        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
        elif view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
        if event:
            data['event_id'] = event.id

    view_kwargs = True
    decorators = (api.has_permission('is_coorganizer', fetch='event_id',
                  fetch_as="event_id", model=CustomForms, methods="POST",), )
    schema = CustomFormSchema
    data_layer = {'session': db.session,
                  'model': CustomForms,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object
                  }}


class CustomFormDetail(ResourceDetail):
    """
    CustomForm Resource
    """

    def before_get_object(self, view_kwargs):
        """
        before get method
        :param view_kwargs:
        :return:
        """
        event = None
        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
        elif view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')

        if event:
            custom_form = safe_query(self, CustomForms, 'event_id', event.id, 'event_id')
            view_kwargs['id'] = custom_form.id

    decorators = (api.has_permission('is_coorganizer', fetch='event_id',
                  fetch_as="event_id", model=CustomForms, methods="PATCH,DELETE"), )
    schema = CustomFormSchema
    data_layer = {'session': db.session,
                  'model': CustomForms}


class CustomFormRelationshipRequired(ResourceRelationship):
    """
    CustomForm Relationship (Required)
    """
    decorators = (jwt_required,)
    methods = ['GET', 'PATCH']
    schema = CustomFormSchema
    data_layer = {'session': db.session,
                  'model': CustomForms}
