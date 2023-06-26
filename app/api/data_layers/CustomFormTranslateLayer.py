from flask_rest_jsonapi.data_layers.base import BaseDataLayer

from app.models.custom_form import CustomForms
from app.models.event import Event
from app.models.custom_form_translate import CustomFormTranslates
from app.api.helpers.db import save_to_db, safe_query_kwargs
from app.api.helpers.query import event_query


class CustomFormTranslateLayer(BaseDataLayer):
    def create_object(self, data, kwargs):
        """
        create_object method for the Charges layer
        charge the user using paypal or stripe
        :param data:
        :param view_kwargs:
        :return:
        """

        customForm = CustomForms()
        customForm.description = data['description']
        customForm.event_id = data['event']
        customForm.field_identifier = data['field_identifier']
        customForm.form = data['form']
        customForm.form_id = data['form_id']
        customForm.is_complex = data['is_complex']
        customForm.is_fixed = data['is_fixed']
        customForm.is_included = data['is_included']
        customForm.is_public = data['is_public']
        customForm.is_required = data['is_required']
        customForm.main_language = data['main_language']
        customForm.max = data['max']
        customForm.min = data['min']
        customForm.name = data['name']
        customForm.position = data['position']
        customForm.type = data['type']
        save_to_db(customForm)

        for item in data['translations']:
            translation = CustomFormTranslates()
            translation.form_id = data['form_id']
            translation.custom_form_id = customForm.id
            translation.name = item['name']
            translation.language_code = item['language_code']
            save_to_db(translation)
        return customForm
