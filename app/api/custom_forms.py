from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.bootstrap import api
from app.api.helpers.db import safe_query, safe_query_kwargs
from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required
from app.api.helpers.query import event_query
from app.api.helpers.utilities import require_relationship
from app.api.schema.custom_forms import CustomFormSchema
from app.models import db
from app.models.custom_form import CUSTOM_FORM_IDENTIFIER_NAME_MAP, CustomForms
from app.models.event import Event


class CustomFormListPost(ResourceList):
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
        if not has_access('is_coorganizer', event_id=data['event']):
            raise ObjectNotFound(
                {'parameter': 'event_id'}, "Event: {} not found".format(data['event_id'])
            )

        # Assign is_complex to True if not found in identifier map of form type
        data['is_complex'] = (
            CUSTOM_FORM_IDENTIFIER_NAME_MAP[data['form']].get(data['field_identifier'])
            is None
        )

    schema = CustomFormSchema
    methods = [
        'POST',
    ]
    data_layer = {'session': db.session, 'model': CustomForms}


class CustomFormList(ResourceList):
    """
    Create and List Custom Forms
    """

    def query(self, view_kwargs):
        """
        query method for different view_kwargs
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(CustomForms)
        query_ = event_query(query_, view_kwargs)
        return query_

    view_kwargs = True
    decorators = (jwt_required,)
    methods = [
        'GET',
    ]
    schema = CustomFormSchema
    data_layer = {
        'session': db.session,
        'model': CustomForms,
        'methods': {'query': query},
    }


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
            event = safe_query_kwargs(Event, view_kwargs, 'event_id')
        elif view_kwargs.get('event_identifier'):
            event = safe_query_kwargs(
                Event,
                view_kwargs,
                'event_identifier',
                'identifier',
            )

        if event:
            custom_form = safe_query(CustomForms, 'event_id', event.id, 'event_id')
            view_kwargs['id'] = custom_form.id

    decorators = (
        api.has_permission(
            'is_coorganizer',
            fetch='event_id',
            model=CustomForms,
            methods="PATCH,DELETE",
        ),
    )
    schema = CustomFormSchema
    data_layer = {
        'session': db.session,
        'model': CustomForms,
        'methods': {'before_get_object': before_get_object},
    }


class CustomFormRelationshipRequired(ResourceRelationship):
    """
    CustomForm Relationship (Required)
    """

    decorators = (
        api.has_permission(
            'is_coorganizer',
            fetch='event_id',
            model=CustomForms,
            methods="PATCH",
        ),
    )
    methods = ['GET', 'PATCH']
    schema = CustomFormSchema
    data_layer = {'session': db.session, 'model': CustomForms}
