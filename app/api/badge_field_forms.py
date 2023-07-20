from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required
from app.api.helpers.utilities import require_relationship
from app.api.schema.badge_field_forms import BadgeFieldFormSchema
from app.models import db
from app.models.badge_field_form import BadgeFieldForms


class BadgeFieldFormList(ResourceList):
    """Create and List Custom Form Translates"""

    def query(self, view_kwargs):
        """
        query method for different view_kwargs
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(BadgeFieldForms)
        if view_kwargs.get('badge_form_id'):
            query_ = query_.filter_by(badge_forms_id=view_kwargs['badge_form_id'])
        return query_

    schema = BadgeFieldFormSchema
    data_layer = {
        'session': db.session,
        'model': BadgeFieldForms,
        'methods': {'query': query},
    }


class BadgeFieldFormDetail(ResourceDetail):
    """BadgeFieldForm Resource Detail"""

    schema = BadgeFieldFormSchema
    data_layer = {'session': db.session, 'model': BadgeFieldForms}


class BadgeFieldFormRelationship(ResourceRelationship):
    """BadgeFieldForm Relationship (Required)"""

    decorators = (jwt_required,)
    methods = ['GET', 'PATCH']
    schema = BadgeFieldFormSchema
    data_layer = {'session': db.session, 'model': BadgeFieldForms}


class BadgeFieldFormListPost(ResourceList):
    """Create and List Custom Form Translates"""

    @staticmethod
    def before_post(data):
        """
        method to check for required relationship with event
        :param data:
        :return:
        """
        require_relationship(['badge_form'], data)
        if not has_access('is_coorganizer', badge_form=data['badge_form']):
            raise ObjectNotFound(
                {'parameter': 'badge_form'},
                f"Custom Form: {data['badge_form']} not found",
            )

    schema = BadgeFieldFormSchema
    methods = [
        'POST',
    ]
    data_layer = {'session': db.session, 'model': BadgeFieldForms}
