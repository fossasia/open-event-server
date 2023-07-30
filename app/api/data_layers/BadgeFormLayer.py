from flask_rest_jsonapi.data_layers.base import BaseDataLayer

from app.api.helpers.db import save_to_db
from app.models.badge_field_form import BadgeFieldForms
from app.models.badge_form import BadgeForms


class BadgeFormLayer(BaseDataLayer):
    """Badge Form Data Layer"""

    @staticmethod
    def create_object(data, _view_kwargs):
        """
        create_object method for the Badge Form Layer
        charge the user using paypal or stripe
        :param data:
        :param _view_kwargs:
        :return:
        """
        badgeForm = BadgeForms()
        keys = [
            'badge_id',
            'badge_size',
            'badge_color',
            'badge_image_url',
            'badge_orientation',
        ]
        for key in keys:
            if key in data:
                badgeForm.__setattr__(key, data[key])

        badgeForm.event_id = data['event']
        save_to_db(badgeForm)

        if 'badge_fields' in data:
            keyBadgeFields = [
                'field_identifier',
                'custom_field',
                'sample_text',
                'font_size',
                'font_name',
                'font_weight',
                'font_color',
                'text_rotation',
                'text_alignment',
                'text_type',
                'margin_top',
                'margin_bottom',
                'margin_left',
                'margin_right',
                'qr_custom_field',
                'is_deleted',
                'is_field_expanded',
            ]
            for item in data['badge_fields']:
                badgeFieldForm = BadgeFieldForms()
                for key in keyBadgeFields:
                    if key in item:
                        badgeFieldForm.__setattr__(key, item[key])

                badgeFieldForm.badge_id = item['badge_id']
                badgeFieldForm.is_deleted = item['is_deleted']
                badgeFieldForm.badge_form_id = badgeForm.id
                save_to_db(badgeFieldForm)
        return badgeForm
