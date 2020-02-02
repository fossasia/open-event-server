from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.schema.custom_form_options import CustomFormOptionSchema
from app.models import db
from app.models.custom_form_option import CustomFormOptions


class CustomFormOptionList(ResourceList):
    """
    Create and List Custom Form Options
    """

    def query(self, view_kwargs):
        query_ = self.session.query(CustomFormOptions)
        if view_kwargs.get('custom_form_id'):
            query_ = self.session.query(CustomFormOptions).filter(
                getattr(CustomFormOptions, 'custom_form_id')
                == view_kwargs['custom_form_id']
            )
        return query_

    schema = CustomFormOptionSchema
    data_layer = {
        'session': db.session,
        'model': CustomFormOptions,
        'methods': {'query': query},
    }


class CustomFormOptionDetail(ResourceDetail):
    """
    CustomForm Resource
    """

    schema = CustomFormOptionSchema
    data_layer = {'session': db.session, 'model': CustomFormOptions}


class CustomFormOptionRelationship(ResourceRelationship):
    """
    CustomForm Resource
    """

    schema = CustomFormOptionSchema
    data_layer = {'session': db.session, 'model': CustomFormOptions}
