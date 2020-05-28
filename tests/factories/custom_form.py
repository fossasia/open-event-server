import factory

import tests.factories.common as common
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic
from app.models.custom_form import CustomForms


class CustomFormFactory(BaseFactory):
    class Meta:
        model = CustomForms

    event = factory.RelatedFactory(EventFactoryBasic)
    form = common.string_
    field_identifier = common.string_
    type = "text"
    is_required = False
    is_included = False
    is_fixed = False
    event_id = 1
