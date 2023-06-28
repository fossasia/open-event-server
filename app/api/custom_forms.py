from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.bootstrap import api
from app.api.data_layers.CustomFormTranslateLayer import CustomFormTranslateLayer
from app.api.helpers.db import safe_query, safe_query_kwargs
from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required
from app.api.helpers.query import event_query
from app.api.helpers.utilities import require_relationship
from app.api.schema.custom_forms import CustomFormSchema
from app.models import db
from app.models.custom_form import CUSTOM_FORM_IDENTIFIER_NAME_MAP, CustomForms
from app.models.custom_form_translate import CustomFormTranslates
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
    data_layer = {
        'class': CustomFormTranslateLayer,
        'session': db.session,
        'model': CustomForms,
    }


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
        if view_kwargs.get('form_id'):
            events = safe_query_kwargs(Event, view_kwargs, 'event_id')
            query_ = self.session.query(CustomForms).filter_by(event_id=events.id)
            query_ = query_.filter_by(form_id=view_kwargs.get('form_id'))
        else:
            query_ = event_query(query_, view_kwargs)
        return query_

    @staticmethod
    def after_get(custom_forms):
        """
        query method for different view_kwargs
        :param view_kwargs:
        :return:
        """
        for item in custom_forms['data']:
            translation = []
            if item['attributes']['is-complex']:
                customFormTranslates = (
                    CustomFormTranslates.query.filter_by(custom_form_id=item['id'])
                    .filter_by(form_id=item['attributes']['form-id'])
                    .all()
                )
                for customFormTranslate in customFormTranslates:
                    translation.append(customFormTranslate.convert_to_dict())
                item['attributes']['translations'] = translation
        return custom_forms

    view_kwargs = True
    decorators = (jwt_required,)
    methods = [
        'GET',
    ]
    schema = CustomFormSchema
    data_layer = {
        'session': db.session,
        'model': CustomForms,
        'methods': {'query': query, 'after_get': after_get},
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

    @staticmethod
    def before_patch(_args, kwargs, data):
        """
        before patch method
        :param _args:
        :param kwargs:
        :param data:
        :return:
        """
        translation = data.get('translations')
        if translation:
            for translate in translation:
                customFormTranslate = None
                if 'id' in translate:
                    customFormTranslate = (
                        CustomFormTranslates.check_custom_form_translate(
                            kwargs['id'], translate['id']
                        )
                    )
                if (
                    customFormTranslate is not None
                    and 'isDeleted' in translate
                    and translate['isDeleted']
                ):
                    db.session.delete(customFormTranslate)
                else:
                    if customFormTranslate:
                        customFormTranslate.name = translate['name']
                        customFormTranslate.language_code = translate['language_code']
                        customFormTranslate.form_id = data['form_id']
                        db.session.add(customFormTranslate)
                    else:
                        customFormTranslate = CustomFormTranslates()
                        customFormTranslate.form_id = data['form_id']
                        customFormTranslate.custom_form_id = kwargs['id']
                        customFormTranslate.name = translate['name']
                        customFormTranslate.language_code = translate['language_code']
                        db.session.add(customFormTranslate)

    @staticmethod
    def before_delete(_obj, kwargs):
        """
        before delete method
        :param _obj:
        :param kwargs:
        :return:
        """
        customFormTranslate = CustomFormTranslates.query.filter_by(
            custom_form_id=kwargs['id']
        ).all()
        for item in customFormTranslate:
            db.session.delete(item)

    @staticmethod
    def after_patch(custom_form):
        """
        after patch method
        :param custom_form:
        :return:
        """
        translation = []
        data = custom_form['data']
        attributes = data['attributes']
        if attributes and attributes['is-complex']:
            customFormTranslates = (
                CustomFormTranslates.query.filter_by(custom_form_id=data['id'])
                .filter_by(form_id=attributes['form-id'])
                .all()
            )
            for customFormTranslate in customFormTranslates:
                translation.append(customFormTranslate.convert_to_dict())
            attributes['translations'] = translation
        return custom_form

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
        'methods': {
            'before_get_object': before_get_object,
            'before_patch': before_patch,
            'before_delete': before_delete,
            'after_patch': after_patch,
        },
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
