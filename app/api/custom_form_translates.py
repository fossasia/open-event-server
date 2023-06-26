from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required
from app.api.helpers.utilities import require_relationship
from app.api.schema.custom_form_translates import CustomFormTranslateSchema
from app.models import db
from app.models.custom_form_translate import CustomFormTranslates


class CustomFormTranslateList(ResourceList):
    """Create and List Custom Form Translates"""

    def query(self, view_kwargs):
        """
        query method for different view_kwargs
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(CustomFormTranslates)
        if view_kwargs.get('custom_form_id'):
            query_ = query_.filter(custom_forms_id=view_kwargs['custom_form_id'])
            if view_kwargs.get('language_code'):
                query_ = query_.filter(language_code=view_kwargs['language_code'])
        return query_

    schema = CustomFormTranslateSchema
    data_layer = {
        'session': db.session,
        'model': CustomFormTranslates,
        'methods': {'query': query},
    }


class CustomFormTranslateDetail(ResourceDetail):
    """CustomFormTranslate Resource Detail"""

    schema = CustomFormTranslateSchema
    data_layer = {'session': db.session, 'model': CustomFormTranslates}


class CustomFormTranslateRelationship(ResourceRelationship):
    """CustomFormTranslate Relationship (Required)"""

    decorators = (jwt_required,)
    methods = ['GET', 'PATCH']
    schema = CustomFormTranslateSchema
    data_layer = {'session': db.session, 'model': CustomFormTranslates}


class CustomFormTranslateListPost(ResourceList):
    """Create and List Custom Form Translates"""

    @staticmethod
    def before_post(data):
        """
        method to check for required relationship with event
        :param data:
        :return:
        """
        require_relationship(['custom_form'], data)
        if not has_access('is_coorganizer', custom_form=data['custom_form']):
            raise ObjectNotFound(
                {'parameter': 'custom_form'},
                f"Custom Form: {data['custom_form']} not found",
            )

    schema = CustomFormTranslateSchema
    methods = [
        'POST',
    ]
    data_layer = {'session': db.session, 'model': CustomFormTranslates}
