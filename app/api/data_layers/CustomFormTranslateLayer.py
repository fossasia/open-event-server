from flask_rest_jsonapi.data_layers.base import BaseDataLayer

from app.api.helpers.db import save_to_db
from app.models.custom_form import CustomForms
from app.models.custom_form_translate import CustomFormTranslates


class CustomFormTranslateLayer(BaseDataLayer):
    """CustomFormTranslate Data Layer"""

    @staticmethod
    def create_object(data, _view_kwargs):
        """
        create_object method for the Charges layer
        charge the user using paypal or stripe
        :param data:
        :param _view_kwargs:
        :return:
        """
        customForm = CustomForms()
        keys = [
            'description',
            'name',
            'form_id',
            'form',
            'is_fixed',
            'is_complex',
            'is_included',
            'is_public',
            'is_required',
            'field_identifier',
            'main_language',
            'max',
            'min',
            'type',
            'position',
            'is_allow_edit',
        ]
        for key in keys:
            if key in data:
                customForm.__setattr__(key, data[key])

        customForm.event_id = data['event']
        save_to_db(customForm)

        if 'translations' in data:
            for item in data['translations']:
                translation = CustomFormTranslates()
                translation.form_id = data['form_id']
                translation.custom_form_id = customForm.id
                translation.name = item['name']
                translation.language_code = item['language_code']
                save_to_db(translation)
        return customForm
