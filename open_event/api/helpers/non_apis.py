"""
API Models and DAOs for models not accessible through API
"""
from flask_restplus import Model

from open_event.models.custom_forms import CustomForms
from open_event.helpers.data import update_or_create

from utils import ServiceDAO
import custom_fields as fields

# #############
# DEFINE MODELS
# #############

CUSTOM_FORM = Model('CustomForm', {
    'id': fields.Integer(),
    'speaker_form': fields.String(),
    'session_form': fields.String()
})

CUSTOM_FORM_POST = CUSTOM_FORM.clone('CustomFormPost')
del CUSTOM_FORM_POST['id']

# ##########
# DEFINE DAO
# ##########


class CFDAO(ServiceDAO):
    def create(self, event_id, data, url):
        data = self.validate(data)
        return update_or_create(self.model, event_id=event_id, **data)

CustomFormDAO = CFDAO(CustomForms, CUSTOM_FORM_POST)
