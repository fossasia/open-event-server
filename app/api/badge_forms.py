from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.bootstrap import api
from app.api.data_layers.BadgeFormLayer import BadgeFormLayer
from app.api.helpers.db import safe_query, safe_query_kwargs
from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required
from app.api.helpers.query import event_query
from app.api.helpers.utilities import require_relationship
from app.api.schema.badge_forms import BadgeFormSchema
from app.models import db
from app.models.badge_field_form import BadgeFieldForms
from app.models.badge_form import BadgeForms
from app.models.event import Event


class BadgeFormList(ResourceList):
    """Create and List Custom Form Translates"""

    def query(self, view_kwargs):
        """
        query method for different view_kwargs
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(BadgeForms)
        if view_kwargs.get('badge_id'):
            events = safe_query_kwargs(Event, view_kwargs, 'event_id')
            query_ = self.session.query(BadgeForms).filter_by(event_id=events.id)
            query_ = query_.filter_by(badge_id=view_kwargs.get('badge_id'))
        else:
            query_ = event_query(query_, view_kwargs)
        return query_

    @staticmethod
    def after_get(badge_forms):
        """
        query method for different view_kwargs
        :param view_kwargs:
        :return:
        """
        for item in badge_forms['data']:
            badgeFields = []
            badgeFieldForms = (
                BadgeFieldForms.query.filter_by(badge_form_id=item['id'])
                .filter_by(badge_id=item['attributes']['badge-id'])
                .order_by(BadgeFieldForms.id.asc())
                .all()
            )
            for badgeFieldForm in badgeFieldForms:
                badgeFields.append(badgeFieldForm.convert_to_dict())
            item['attributes']['badge-fields'] = badgeFields
        return badge_forms

    view_kwargs = True
    decorators = (jwt_required,)
    methods = [
        'GET',
    ]
    schema = BadgeFormSchema
    data_layer = {
        'session': db.session,
        'model': BadgeForms,
        'methods': {'query': query, 'after_get': after_get},
    }


class BadgeFormDetail(ResourceDetail):
    """BadgeForm Resource Detail"""

    @staticmethod
    def before_get_object(view_kwargs):
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
            badge_form = safe_query(BadgeForms, 'event_id', event.id, 'event_id')
            view_kwargs['id'] = badge_form.id

    @staticmethod
    def before_patch(_args, kwargs, data):
        """
        before patch method
        :param _args:
        :param kwargs:
        :param data:
        :return:
        """
        badgeFields = data.get('badge_fields')
        if badgeFields:
            for badgeField in badgeFields:
                badgeFieldForm = None
                if 'badge_field_id' in badgeField:
                    badgeFieldForm = BadgeFieldForms.get_badge_field_form_if_exist(
                        badgeField['badge_field_id'], badgeField['badge_id']
                    )
                if (
                    badgeFieldForm is not None
                    and 'is_deleted' in badgeField
                    and badgeField['is_deleted']
                ):
                    db.session.delete(badgeFieldForm)
                else:
                    if badgeFieldForm:
                        badgeFieldForm.badge_id = data['badge_id']
                    else:
                        badgeFieldForm = BadgeFieldForms()
                        badgeFieldForm.badge_id = data['badge_id']

                    badgeFieldForm.badge_form_id = kwargs['id']
                    badgeFieldForm.field_identifier = badgeField['field_identifier']
                    badgeFieldForm.custom_field = badgeField['custom_field']
                    badgeFieldForm.sample_text = badgeField['sample_text']
                    badgeFieldForm.font_name = badgeField['font_name']
                    badgeFieldForm.font_size = badgeField['font_size']
                    badgeFieldForm.font_color = badgeField['font_color']
                    badgeFieldForm.font_weight = badgeField.get('font_weight')
                    badgeFieldForm.text_rotation = badgeField['text_rotation']
                    badgeFieldForm.text_alignment = badgeField['text_alignment']
                    badgeFieldForm.text_type = badgeField['text_type']
                    badgeFieldForm.margin_top = badgeField['margin_top']
                    badgeFieldForm.margin_bottom = badgeField['margin_bottom']
                    badgeFieldForm.margin_left = badgeField['margin_left']
                    badgeFieldForm.margin_right = badgeField['margin_right']
                    badgeFieldForm.qr_custom_field = badgeField.get('qr_custom_field')
                    badgeFieldForm.is_deleted = badgeField['is_deleted']
                    badgeFieldForm.is_field_expanded = badgeField['is_field_expanded']
                    db.session.add(badgeFieldForm)

    @staticmethod
    def before_delete(_obj, kwargs):
        """
        before delete method
        :param _obj:
        :param kwargs:
        :return:
        """
        badgeFieldForm = BadgeFieldForms.query.filter_by(badge_form_id=kwargs['id']).all()
        for item in badgeFieldForm:
            db.session.delete(item)

    @staticmethod
    def after_patch(badge_form):
        """
        after patch method
        :param badge_form:
        :return:
        """
        badgeFields = []
        data = badge_form['data']
        attributes = data['attributes']
        badgeFieldForms = (
            BadgeFieldForms.query.filter_by(badge_form_id=data['id'])
            .filter_by(badge_id=attributes['badge-id'])
            .all()
        )
        for badgeFieldForm in badgeFieldForms:
            badgeFields.append(badgeFieldForm.convert_to_dict())
        attributes['badge-fields'] = badgeFields
        return badge_form

    decorators = (
        api.has_permission(
            'is_coorganizer',
            fetch='event_id',
            model=BadgeForms,
            methods="PATCH,DELETE",
        ),
    )
    schema = BadgeFormSchema
    data_layer = {
        'session': db.session,
        'model': BadgeForms,
        'methods': {
            'before_patch': before_patch,
            'before_delete': before_delete,
            'after_patch': after_patch,
        },
    }


class BadgeFormRelationship(ResourceRelationship):
    """BadgeForm Relationship (Required)"""

    decorators = (jwt_required,)
    methods = ['GET', 'PATCH']
    schema = BadgeFormSchema
    data_layer = {'session': db.session, 'model': BadgeForms}


class BadgeFormListPost(ResourceList):
    """Create and List Custom Form Translates"""

    @staticmethod
    def before_post(_args, _kwargs, data):
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
                {'parameter': 'event_id'},
                f"Event: {data['event_id']} not found",
            )

    schema = BadgeFormSchema
    methods = [
        'POST',
    ]
    data_layer = {'class': BadgeFormLayer, 'session': db.session, 'model': BadgeForms}
